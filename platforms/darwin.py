"""macOS-specific implementations of the SPort platform layer.

Provides:

* :class:`Autostart` — ``~/Library/LaunchAgents/<app_id>.plist``.
* :class:`DarwinNotifier` — desktop notifications via ``plyer`` (osascript).
* :func:`get_system_registry` — macOS system processes and accounts.

PPL-equivalent concept doesn't exist on macOS — all processes are visible to
the owner without elevation (modulo SIP-protected daemons, which still report
name + PID to psutil). :func:`get_protected_process_info` is therefore
absent and callers must treat it as ``None`` on this platform.
"""
from __future__ import annotations

import os
import plistlib
import sys
from typing import Any, Dict, Optional

from ._common import AutostartController, Notifier as BaseNotifier, SystemProcessRegistry

PLATFORM_NAME = "darwin"


# ---------------------------------------------------------------------------
# Autostart (LaunchAgent)
# ---------------------------------------------------------------------------
class Autostart(AutostartController):
    PLIST_DIR = os.path.expanduser("~/Library/LaunchAgents")

    @property
    def plist_path(self) -> str:
        return os.path.join(self.PLIST_DIR, f"{self.app_id}.plist")

    def _program_arguments(self):
        args = []
        if getattr(sys, "frozen", False):
            args.append(sys.executable)
        else:
            script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tray.py"))
            args.extend([sys.executable, script])
        args.append("--silent")
        return args

    def is_enabled(self) -> bool:
        return os.path.exists(self.plist_path)

    def set_enabled(self, enabled: bool) -> bool:
        if not enabled:
            try:
                os.remove(self.plist_path)
            except FileNotFoundError:
                pass
            return True
        try:
            os.makedirs(self.PLIST_DIR, exist_ok=True)
            plist = {
                "Label": self.app_id,
                "ProgramArguments": self._program_arguments(),
                "RunAtLoad": True,
                "ProcessType": "Interactive",
                "KeepAlive": False,
            }
            with open(self.plist_path, "wb") as f:
                plistlib.dump(plist, f)
            return True
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Notifications (plyer -> osascript)
# ---------------------------------------------------------------------------
class Notifier(BaseNotifier):
    def __init__(self, app_id: str, app_name: str):
        super().__init__(app_id, app_name)
        try:
            from plyer import notification  # type: ignore
            self._notification = notification
            self._available = True
        except ImportError:
            self._notification = None
            self._available = False

    def notify(self, title: str, message: str, icon_path: Optional[str] = None) -> bool:
        if not self._available:
            return False
        try:
            self._notification.notify(
                title=title,
                message=message,
                app_name=self.app_name,
                app_icon=icon_path or "",
                timeout=5,
            )
            return True
        except Exception:
            return False


# ---------------------------------------------------------------------------
# System process registry
# ---------------------------------------------------------------------------
DARWIN_SYSTEM_PROCESSES = {
    # Kernel / launchd
    "kernel_task", "launchd",
    # Window server / login
    "WindowServer", "loginwindow", "iconservicesagent",
    "CoreServicesUIAgent", "SystemUIServer", "WallpaperAgent",
    # Audio
    "coreaudiod", "coreaudio", "audioclocksd",
    # File system / indexing
    "Finder", "Dock", "cfprefsd", "mds_stores", "mds",
    "mdworker_shared", "mdworker", "mdworker_helper",
    "diskarbitrationd", "fseventsd", "deleted", "revisiond",
    "bird", "cloudd", "CloudKitDaemon", "CloudTelemetryService",
    "nsurlsessiond", "nsurlstoraged",
    # Security / privacy
    "trustd", "securityd", "SymptomReporter", "dasd",
    "notifyd", "taskgated", "amfid", "syspolicyd",
    # Network
    "networkd", "networkserviceproxy", "symptomsd", "analyticsd",
    "osanalyticshelper", "mDNSResponder", "configd",
    # Power / input
    "powerd", "thermalmonitord", "hidd", "IOKit",
    "kbd", "displayrepl", "displaypolicyd",
    # Print
    "cupsd", "cups-notifyd", "printtool",
    # User event / app launching
    "UserEventAgent", "launchservicesd", "lsd",
    "runningboardd", "rtcreportingd", "timed",
    # Spotlight / Siri
    "siriknowledged", "assistant_service", "parsec-fbf",
    "Suggest", "suggestd",
    # Misc Apple
    "Fontd", "universalaccessd", "warmd",
    "containermanagerd", "logd", "awdd", "sosyphusd",
    "SubmitDiagInfo", "OSAnalytics", "locationd",
    "lifecycleagentd", "sharingd", "pboard",
    "TextInputMenuAgent", "TextInputSwitcher", "TCC", "tccd",
    "xpcd", "xpcproxy", "SIServer",
    "AMPDeviceDiscoveryAgent", "RapportUtilService",
    "ContinuityDownloader", "ContextStoreAgent",
    "SpeechSynthesisServer", "SpeechRecognitionServer",
    "IMDPersistenceAgent", "distnoted", "usernoted",
    "IMAutoPullAgent", "IMDMessageServicesAgent",
    "com.apple.MobileSync", "MobileSync", "MobileBackup",
    "nsappproxy", "NEQMTLLoader", "nesessionmanager",
    "com.apple.WebKit.Networking", "com.apple.WebKit.WebContent",
    "WebKit", "Safari", "safaridriver",
    "containermanagerd", "Containermanagerd",
    "StorageKit", "ParentalControls", "familycircled",
    "biokitd", "biokitagent", "biometrickitd",
    "rapportd", "IMTransferAgent", "AirPlayXPCHelper",
    "com.apple.CoreDevice.remotepairing", "remotepairing",
    "screensaver", "loginwindow", "auecc", "AUUC",
    "TimeMachine", "backupd", "fsck_msdos",
}

DARWIN_SYSTEM_USERS = {
    "root",
    "_mdnsresponder", "_locationd", "_coreaudiod",
    "_windowserver", "_securityd", "_usbmuxd", "_driverkit",
    "_hidd", "_networkserviceproxy", "_analyticsd",
    "_timed", "_cmiodalassistants", "_displayrepl",
    "_iconservices", "_iconservicesagent", "_installcoordinationd",
    "_gamecontrollerd", "_findmydeviced", "_findmydevice",
    "_accessibilityaudiod", "_appstore", "_corecapture",
    "_displaypolicyd", "_fpsd", "_gamecontrollerd",
    "_helpd", "_logd", "_mailrelay", "_mbsetupuser",
    "_neagent", "_networkd", "_nsurlsessiond", "_nsurlstoraged",
    "_ondemand", "_powerd", "_reportmemoryexception",
    "_sandbox", "_sntp", "_softwareupdate", "_spotlight",
    "_sshd", "_sysadmin", "_sysdiagnose", "_syslogd",
    "_system_group", "_taskgated", "_trustd", "_usbmuxd",
    "_www", "_xgridagent", "_xgridcontrollerd",
}


def get_system_registry() -> SystemProcessRegistry:
    return SystemProcessRegistry(DARWIN_SYSTEM_PROCESSES, DARWIN_SYSTEM_USERS)


def get_protected_process_info(pid: int) -> Optional[Dict[str, Any]]:
    """No PPL concept on macOS; psutil covers everything we need."""
    return None
