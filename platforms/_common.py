"""Cross-platform base classes and shared helpers for SPort.

The :mod:`platforms` package selects one of :mod:`platforms.windows`,
:mod:`platforms.darwin`, or :mod:`platforms.linux` at import time based on
``sys.platform``. Callers should import from :mod:`platforms` only — never
from the per-OS submodules — so the abstraction stays opaque.

Each platform provides the same surface:

* ``Autostart`` (subclass of :class:`AutostartController`) — read/write the
  per-user autostart entry.
* ``Notifier`` (subclass of :class:`Notifier`) — desktop notifications.
* ``get_system_registry()`` — returns a :class:`SystemProcessRegistry` with
  the well-known system process names and system accounts for that OS.
* ``get_protected_process_info(pid)`` (Windows only) — best-effort info for
  PPL/AntiMalware processes. Returns ``None`` on other platforms.

The :class:`SingleInstance` lock is shared across all platforms — it uses a
localhost TCP socket so it works on every supported OS without extra deps.
"""
from __future__ import annotations

import abc
import os
import socket
import sys
import threading
import time
from typing import Callable, Optional


# ---------------------------------------------------------------------------
# Autostart
# ---------------------------------------------------------------------------
class AutostartController(abc.ABC):
    """Read/write the autostart entry for the current user."""

    def __init__(self, app_name: str, app_id: str):
        self.app_name = app_name
        self.app_id = app_id  # reverse-DNS, used as plist label / .desktop filename

    @abc.abstractmethod
    def is_enabled(self) -> bool: ...

    @abc.abstractmethod
    def set_enabled(self, enabled: bool) -> bool: ...


# ---------------------------------------------------------------------------
# Single instance (lock + IPC, cross-platform via TCP localhost)
# ---------------------------------------------------------------------------
class SingleInstance:
    """Cross-platform single-instance lock using a TCP socket on localhost.

    The first instance binds ``127.0.0.1:lock_port`` and listens for one-line
    commands (terminated by ``\\n``). Subsequent instances detect the
    existing lock, send a command via a short TCP connection, and exit.
    """

    DEFAULT_LOCK_PORT = 17777  # companion to dashboard port 7777
    RECONNECT_DELAY = 0.1
    RECONNECT_TIMEOUT = 2.0
    BUFFER = 4096

    def __init__(self, name: str = "SPort", lock_port: int = DEFAULT_LOCK_PORT):
        self.name = name
        self.lock_port = lock_port
        self._sock: Optional[socket.socket] = None
        self._server_thread: Optional[threading.Thread] = None
        self._server_running = False
        self.is_first = self._acquire()

    def _acquire(self) -> bool:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # On Windows, ``SO_REUSEADDR`` allows rebinding to a port that is
        # currently in use (different from Unix semantics). Use
        # ``SO_EXCLUSIVEADDRUSE`` to make the bind truly exclusive.
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            s.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        else:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("127.0.0.1", self.lock_port))
            s.listen(8)
        except OSError:
            s.close()
            return False
        self._sock = s
        return True

    def send_command(self, command: str, timeout: float = RECONNECT_TIMEOUT) -> bool:
        """Send a one-line command to the running instance. Returns False if we
        are the first instance, or if the running instance can't be reached.
        """
        if self.is_first:
            return False
        deadline = time.time() + timeout
        data = command.encode("utf-8") + b"\n"
        while time.time() < deadline:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                s.connect(("127.0.0.1", self.lock_port))
                try:
                    s.sendall(data)
                finally:
                    s.close()
                return True
            except OSError:
                time.sleep(self.RECONNECT_DELAY)
        return False

    def start_server(self, callback: Callable[[str], None]) -> None:
        if not self.is_first or self._sock is None:
            return
        self._server_running = True
        self._server_thread = threading.Thread(
            target=self._server_loop, args=(callback,), daemon=True,
        )
        self._server_thread.start()

    def _server_loop(self, callback: Callable[[str], None]) -> None:
        assert self._sock is not None
        sock = self._sock
        while self._server_running:
            try:
                sock.settimeout(0.5)
                try:
                    conn, _ = sock.accept()
                except socket.timeout:
                    continue
                except OSError:
                    if not self._server_running:
                        break
                    time.sleep(self.RECONNECT_DELAY)
                    continue
                with conn:
                    conn.settimeout(1.0)
                    buf = b""
                    while not buf.endswith(b"\n") and len(buf) < self.BUFFER:
                        try:
                            chunk = conn.recv(self.BUFFER - len(buf))
                        except OSError:
                            break
                        if not chunk:
                            break
                        buf += chunk
                    command = buf.decode("utf-8", errors="ignore").strip()
                    if command and callback:
                        try:
                            callback(command)
                        except Exception:
                            pass
            except Exception:
                time.sleep(self.RECONNECT_DELAY)

    def stop_server(self) -> None:
        self._server_running = False

    def release(self) -> None:
        self.stop_server()
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------
class Notifier(abc.ABC):
    """Cross-platform desktop notification dispatcher."""

    def __init__(self, app_id: str, app_name: str):
        self.app_id = app_id
        self.app_name = app_name

    @abc.abstractmethod
    def notify(self, title: str, message: str, icon_path: Optional[str] = None) -> bool: ...


# ---------------------------------------------------------------------------
# System process registry
# ---------------------------------------------------------------------------
class SystemProcessRegistry:
    """Per-platform list of well-known system processes and accounts.

    Process names are matched case-insensitive; the ``.exe`` suffix is
    ignored on input (so ``svchost`` matches ``svchost.exe``).
    """

    def __init__(self, processes, users):
        self._processes = {p.lower() for p in processes}
        self._users = {u.upper() for u in users}

    def is_system_process(self, name: str) -> bool:
        if not name:
            return False
        n = name.lower()
        if n in self._processes:
            return True
        base = n[:-4] if n.endswith(".exe") else n
        for p in self._processes:
            p_base = p[:-4] if p.endswith(".exe") else p
            if base == p_base:
                return True
        return False

    def is_system_user(self, user: str) -> bool:
        return bool(user) and user.upper() in self._users

    @property
    def processes(self):
        return sorted(self._processes)

    @property
    def users(self):
        return sorted(self._users)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def repo_command_line(*extra_args: str) -> str:
    """Build the command line to launch SPort from a source checkout."""
    script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tray.py"))
    parts = [f'"{sys.executable}"', f'"{script}"', *extra_args]
    return " ".join(parts)
