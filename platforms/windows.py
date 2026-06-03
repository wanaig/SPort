"""Windows-specific implementations of the SPort platform layer.

Provides:

* :class:`Autostart` — HKCU\\...\\Run registry key.
* :class:`WindowsNotifier` — toast notifications via ``winotify``.
* :func:`get_system_registry` — Windows system processes and accounts.
* :func:`get_protected_process_info` — best-effort info for PPL/AntiMalware
  processes via ``Toolhelp32`` + ``OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION)``.
"""
from __future__ import annotations

import ctypes
import os
import sys
import time
from ctypes import wintypes
from typing import Any, Dict, Optional

from ._common import (
    AutostartController,
    Notifier as BaseNotifier,
    SystemProcessRegistry,
)

PLATFORM_NAME = "windows"

try:
    import winreg
    _HAS_WINREG = True
except ImportError:
    _HAS_WINREG = False

# ---------------------------------------------------------------------------
# Autostart (HKCU\...\Run)
# ---------------------------------------------------------------------------
class Autostart(AutostartController):
    REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

    def _command_line(self) -> str:
        if getattr(sys, "frozen", False):
            return f'"{sys.executable}" --silent'
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tray.py"))
        return f'"{_pythonw()}" "{script_path}" --silent'

    def is_enabled(self) -> bool:
        if not _HAS_WINREG:
            return False
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.REG_PATH, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, self.app_name)
                return bool(value)
        except FileNotFoundError:
            return False
        except OSError:
            return False
        except Exception:
            return False

    def set_enabled(self, enabled: bool) -> bool:
        if not _HAS_WINREG:
            return False
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.REG_PATH, 0, winreg.KEY_SET_VALUE) as key:
                if enabled:
                    winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, self._command_line())
                else:
                    try:
                        winreg.DeleteValue(key, self.app_name)
                    except FileNotFoundError:
                        pass
            return True
        except Exception:
            return False


def _pythonw() -> str:
    """Locate ``pythonw.exe`` next to the current Python — avoids the
    console window when autostart runs SPort."""
    if getattr(sys, "frozen", False):
        return sys.executable
    python_dir = os.path.dirname(sys.executable)
    pythonw = os.path.join(python_dir, "pythonw.exe")
    return pythonw if os.path.exists(pythonw) else sys.executable


# ---------------------------------------------------------------------------
# Notifications (winotify)
# ---------------------------------------------------------------------------
class Notifier(BaseNotifier):
    def __init__(self, app_id: str, app_name: str):
        super().__init__(app_id, app_name)
        try:
            from winotify import Notification, audio as toast_audio  # type: ignore
            self._Notification = Notification
            self._audio = toast_audio
            self._available = True
        except ImportError:
            self._Notification = None
            self._audio = None
            self._available = False

    def notify(self, title: str, message: str, icon_path: Optional[str] = None) -> bool:
        if not self._available:
            return False
        try:
            toast = self._Notification(
                app_id=self.app_id,
                title=title,
                msg=message,
                duration="short",
                icon=icon_path or "",
            )
            toast.set_audio(self._audio.Default, loop=False)
            toast.show()
            return True
        except Exception:
            return False


# ---------------------------------------------------------------------------
# System process registry
# ---------------------------------------------------------------------------
WINDOWS_SYSTEM_PROCESSES = {
    "System", "[System Process]", "Secure System", "Registry",
    # Core
    "smss.exe", "csrss.exe", "wininit.exe", "winlogon.exe",
    "services.exe", "lsass.exe", "lsaiso.exe", "lsm.exe",
    "userinit.exe", "LogonUI.exe",
    # Service hosts and broker
    "svchost.exe", "WmiPrvSE.exe", "WmiApSrv.exe", "taskhostw.exe",
    "taskhostex.exe", "RuntimeBroker.exe", "dllhost.exe",
    "audiodg.exe", "fontdrvhost.exe", "conhost.exe", "dashost.exe",
    # Search / shell / UI
    "SearchHost.exe", "SearchIndexer.exe", "SearchProtocolHost.exe",
    "SearchFilterHost.exe", "ShellExperienceHost.exe",
    "StartMenuExperienceHost.exe", "TextInputHost.exe", "LockApp.exe",
    "smartscreen.exe",
    # Drivers / kernel helpers
    "WerFault.exe", "WerFaultSecure.exe", "WUDFHost.exe", "WUDFPlatform.exe",
    # Security
    "SecurityHealthService.exe", "MsMpEng.exe", "NisSrv.exe",
    "MpCmdRun.exe",
    # Printing / networking
    "spoolsv.exe", "ismserv.exe", "efssvc.exe", "esifsvc.exe",
    # OEM/vendor bloat (commonly safe to hide)
    "IntelAudioService.exe", "NahimicService.exe", "NahimicSvc.exe",
    "RtkAudUService64.exe", "RazerCentralService.exe",
}

WINDOWS_SYSTEM_USERS = {
    "NT AUTHORITY\\SYSTEM",
    "NT AUTHORITY\\LOCAL SERVICE",
    "NT AUTHORITY\\NETWORK SERVICE",
    "SYSTEM", "LOCAL SERVICE", "NETWORK SERVICE",
}


def get_system_registry() -> SystemProcessRegistry:
    return SystemProcessRegistry(WINDOWS_SYSTEM_PROCESSES, WINDOWS_SYSTEM_USERS)


# ---------------------------------------------------------------------------
# Protected process info (PPL / AntiMalware)
# ---------------------------------------------------------------------------
_TOOLHELP_CACHE: Dict[str, Any] = {"data": {}, "ts": 0.0}
_TOOLHELP_TTL = 15.0


def _build_pe32w():
    class PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("th32DefaultHeapID", ctypes.POINTER(wintypes.ULONG)),
            ("th32ModuleID", wintypes.DWORD),
            ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD),
            ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", wintypes.DWORD),
            ("szExeFile", ctypes.c_wchar * 260),
        ]
    return PROCESSENTRY32W


def _refresh_toolhelp() -> Dict[int, str]:
    """Snapshot of {pid: process_name} using ``Toolhelp32``. Works for
    PPL/AntiMalware processes that ``psutil`` can't see."""
    now = time.time()
    if _TOOLHELP_CACHE["data"] and (now - _TOOLHELP_CACHE["ts"]) < _TOOLHELP_TTL:
        return _TOOLHELP_CACHE["data"]

    data: Dict[int, str] = {}
    try:
        kernel32 = ctypes.windll.kernel32
        TH32CS_SNAPPROCESS = 0x00000002
        PE32W = _build_pe32w()
        snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if snapshot and snapshot != -1:
            try:
                entry = PE32W()
                entry.dwSize = ctypes.sizeof(entry)
                if kernel32.Process32FirstW(snapshot, ctypes.byref(entry)):
                    while True:
                        data[entry.th32ProcessID] = entry.szExeFile
                        if not kernel32.Process32NextW(snapshot, ctypes.byref(entry)):
                            break
            finally:
                kernel32.CloseHandle(snapshot)
    except Exception:
        pass

    _TOOLHELP_CACHE["data"] = data
    _TOOLHELP_CACHE["ts"] = now
    return data


def _get_exe_limited(pid: int) -> Optional[str]:
    """Get full exe path with ``PROCESS_QUERY_LIMITED_INFORMATION`` —
    works for some PPL where ``psutil.Process.exe()`` is denied."""
    if not pid:
        return None
    try:
        kernel32 = ctypes.windll.kernel32
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return None
        try:
            buf = ctypes.create_unicode_buffer(1024)
            size = wintypes.DWORD(1024)
            if kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
                return buf.value
        finally:
            kernel32.CloseHandle(handle)
    except Exception:
        return None
    return None


def get_protected_process_info(pid: int) -> Optional[Dict[str, Any]]:
    """Best-effort fallback for processes that ``psutil.Process(pid)`` can't
    open. Returns a partial-info dict, or ``None`` if nothing is recoverable.
    """
    if not pid:
        return None
    name = _refresh_toolhelp().get(pid)
    exe = _get_exe_limited(pid) or ""
    if not name and not exe:
        return None
    return {
        "name": name or f"(pid {pid})",
        "exe": exe,
        "username": "",
        "create_time": 0,
        "partial": True,
    }
