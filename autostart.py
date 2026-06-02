"""Read/write the Windows Run registry key for SPort autostart.

Per-user (HKCU), no admin required. Stored value is the full command line
including --silent so the tray starts without auto-opening the browser.
"""
import os
import sys
import winreg

APP_NAME = "SPort"
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _command_line():
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}" --silent'
    script = os.path.abspath(os.path.join(os.path.dirname(__file__), "tray.py"))
    python_dir = os.path.dirname(sys.executable)
    pythonw = os.path.join(python_dir, "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable
    return f'"{pythonw}" "{script}" --silent'


def is_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            return bool(value)
    except FileNotFoundError:
        return False
    except Exception:
        return False


def set_enabled(enabled):
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE
        ) as key:
            if enabled:
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _command_line())
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
        return True
    except Exception:
        return False
