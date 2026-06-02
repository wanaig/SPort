"""Single-instance lock for SPort using Windows mutex + named pipe.

Second instance detects the running one and sends a command to it
(e.g. "show") instead of starting a duplicate server.
"""
import sys
import time
import threading

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    import win32event
    import win32pipe
    import win32file
    import win32api
    import winerror
else:
    raise ImportError("singleinstance is Windows-only; use a no-op on other platforms")


PIPE_BUFFER = 4096
PIPE_RETRY_DELAY = 0.1
PIPE_RETRY_TIMEOUT = 2.0


class SingleInstance:
    def __init__(self, name="SPort"):
        self.name = name
        self.mutex_name = f"Global\\{name}_SingleInstance_v1"
        self.pipe_name = f"{name}_IPC"
        self.mutex = None
        self._server_thread = None
        self._server_running = False
        self._acquire()

    def _acquire(self):
        self.mutex = win32event.CreateMutex(None, False, self.mutex_name)
        last_err = win32api.GetLastError()
        self.is_first = (last_err != winerror.ERROR_ALREADY_EXISTS)

    @property
    def first(self):
        return self.is_first

    def send_command(self, command, timeout=PIPE_RETRY_TIMEOUT):
        if self.is_first:
            return False
        full_pipe = f"\\\\.\\pipe\\{self.pipe_name}"
        deadline = time.time() + timeout
        data = command.encode("utf-8")
        while time.time() < deadline:
            try:
                handle = win32file.CreateFile(
                    full_pipe,
                    win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                    0,
                    None,
                    win32file.OPEN_EXISTING,
                    0,
                    None,
                )
                try:
                    win32file.WriteFile(handle, data)
                finally:
                    win32file.CloseHandle(handle)
                return True
            except Exception:
                time.sleep(PIPE_RETRY_DELAY)
        return False

    def start_server(self, callback):
        if not self.is_first:
            return
        self._server_running = True
        self._server_thread = threading.Thread(
            target=self._server_loop, args=(callback,), daemon=True
        )
        self._server_thread.start()

    def _server_loop(self, callback):
        full_pipe = f"\\\\.\\pipe\\{self.pipe_name}"
        while self._server_running:
            handle = None
            try:
                handle = win32pipe.CreateNamedPipe(
                    full_pipe,
                    win32pipe.PIPE_ACCESS_DUPLEX,
                    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                    1,
                    PIPE_BUFFER,
                    PIPE_BUFFER,
                    0,
                    None,
                )
                win32pipe.ConnectNamedPipe(handle, None)
                try:
                    result, raw = win32file.ReadFile(handle, PIPE_BUFFER)
                    command = raw.decode("utf-8", errors="ignore").strip()
                    if command and callback:
                        try:
                            callback(command)
                        except Exception:
                            pass
                finally:
                    try:
                        win32pipe.DisconnectNamedPipe(handle)
                    except Exception:
                        pass
                    win32file.CloseHandle(handle)
                    handle = None
            except Exception:
                if handle:
                    try:
                        win32file.CloseHandle(handle)
                    except Exception:
                        pass
                time.sleep(PIPE_RETRY_DELAY)

    def stop_server(self):
        self._server_running = False

    def release(self):
        self.stop_server()
        if self.mutex:
            try:
                win32api.CloseHandle(self.mutex)
            except Exception:
                pass
            self.mutex = None
