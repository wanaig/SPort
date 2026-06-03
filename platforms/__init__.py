"""Cross-platform adapter layer for SPort.

Selects :mod:`platforms.windows`, :mod:`platforms.darwin`, or
:mod:`platforms.linux` at import time based on ``sys.platform``. All callers
should import from this module — never from the per-OS submodules directly.

Exposes four factory functions:

* :func:`get_autostart` — :class:`~platforms._common.AutostartController`
* :func:`get_singleinstance` — :class:`~platforms._common.SingleInstance`
* :func:`get_notifier` — :class:`~platforms._common.Notifier`
* :func:`get_system_registry` — :class:`~platforms._common.SystemProcessRegistry`

Plus one helper for the PPL/AntiMalware fallback that only Windows has:

* :func:`get_protected_process_info` — returns ``None`` on macOS/Linux.
"""
from __future__ import annotations

import sys as _sys
from typing import Any, Dict, Optional

from ._common import (
    AutostartController,
    Notifier,
    SingleInstance,
    SystemProcessRegistry,
)

APP_NAME = "SPort"
APP_ID = "com.wanaig.sport"

# --- platform selection -----------------------------------------------------
if _sys.platform == "win32":
    from . import windows as _impl
elif _sys.platform == "darwin":
    from . import darwin as _impl
elif _sys.platform.startswith("linux") or _sys.platform.startswith("freebsd"):
    from . import linux as _impl
else:
    # Unknown Unix-likes fall back to Linux behavior.
    from . import linux as _impl

PLATFORM_NAME: str = _impl.PLATFORM_NAME
IS_WINDOWS: bool = PLATFORM_NAME == "windows"
IS_MACOS: bool = PLATFORM_NAME == "darwin"
IS_LINUX: bool = PLATFORM_NAME == "linux"


# --- public factories --------------------------------------------------------
def get_autostart() -> AutostartController:
    """Return the autostart controller for the current platform."""
    return _impl.Autostart(APP_NAME, APP_ID)


def get_singleinstance(name: str = APP_NAME, lock_port: int = SingleInstance.DEFAULT_LOCK_PORT) -> SingleInstance:
    """Return a single-instance lock, bound to a stable localhost TCP port."""
    return SingleInstance(name=name, lock_port=lock_port)


def get_notifier() -> Notifier:
    """Return the notification dispatcher for the current platform."""
    return _impl.Notifier(APP_ID, APP_NAME)


def get_system_registry() -> SystemProcessRegistry:
    """Return the system-process registry for the current platform."""
    return _impl.get_system_registry()


def get_protected_process_info(pid: int) -> Optional[Dict[str, Any]]:
    """Best-effort fallback for processes psutil can't open. Windows only;
    returns ``None`` on macOS/Linux (psutil covers everything we need).
    """
    return getattr(_impl, "get_protected_process_info", lambda _pid: None)(pid)
