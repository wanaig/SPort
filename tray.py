"""SPort tray entry point — starts Flask in a background thread and shows a
pystray icon for control. All cross-platform concerns (single-instance lock,
autostart, notifications) are handled by the :mod:`platforms` package.

Second-instance behavior: a second launch detects the running instance via
the platform lock, forwards a ``show`` command to it, and exits.
"""
import os
import sys
import time
import threading
import webbrowser
import atexit
import urllib.request
import json

from app import app
from platforms import (
    get_autostart,
    get_singleinstance,
    get_notifier,
)

import pystray
from PIL import Image, ImageDraw


def _parse_args():
    port = int(os.environ.get("PORT", 7777))
    host = os.environ.get("HOST", "127.0.0.1")
    silent = False
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--port" and i + 1 < len(args):
            port = int(args[i + 1])
            i += 2
        elif a.startswith("--port="):
            port = int(a.split("=", 1)[1])
            i += 1
        elif a == "--host" and i + 1 < len(args):
            host = args[i + 1]
            i += 2
        elif a.startswith("--host="):
            host = a.split("=", 1)[1]
            i += 1
        elif a == "--silent":
            silent = True
            i += 1
        else:
            i += 1
    return host, port, silent


HOST, PORT, SILENT = _parse_args()
DASHBOARD_URL = f"http://{HOST}:{PORT}"


def bundle_root():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


app.template_folder = os.path.join(bundle_root(), "templates")
app.static_folder = os.path.join(bundle_root(), "static")

# Single-instance: lock port mirrors dashboard port to avoid collisions
# (e.g. dashboard 7777 -> lock 17777, dashboard 9999 -> lock 19999).
_instance = get_singleinstance(name="SPort", lock_port=PORT + 10000)
atexit.register(_instance.release)

if not _instance.is_first:
    _instance.send_command("show")
    print("SPort is already running. Opening dashboard in browser...")
    sys.exit(0)

state = {
    "paused": False,
    "notifications": False,
}

_autostart = get_autostart()
_notifier = get_notifier()


def run_server():
    try:
        app.run(host=HOST, port=PORT, debug=False, threaded=True, use_reloader=False)
    except SystemExit:
        raise
    except Exception as e:
        print(f"Server error: {e}")
        os._exit(1)


_server_thread = threading.Thread(target=run_server, daemon=True)
_server_thread.start()

_ready = False
for _ in range(20):
    time.sleep(0.1)
    try:
        urllib.request.urlopen(f"{DASHBOARD_URL}/api/ports", timeout=0.5)
        _ready = True
        break
    except Exception:
        pass

if not _ready:
    print(f"Failed to bind to {DASHBOARD_URL}. Port may be in use.")
    os._exit(1)


def open_dashboard(icon=None, item=None):
    try:
        webbrowser.open(DASHBOARD_URL)
    except Exception:
        pass


def quit_app(icon, item):
    icon.stop()


def toggle_pause(icon, item):
    state["paused"] = not state["paused"]
    app.config["SPORT_PAUSED"] = state["paused"]
    icon.update_menu()


def toggle_autostart(icon, item):
    new = not _autostart.is_enabled()
    _autostart.set_enabled(new)
    icon.update_menu()


def toggle_notifications(icon, item):
    state["notifications"] = not state["notifications"]
    app.config["SPORT_NOTIFY"] = state["notifications"]
    if state["notifications"]:
        if _notification_thread is None or not _notification_thread.is_alive():
            _notification_stop.clear()
            t = threading.Thread(target=notification_loop, args=(_notification_stop,), daemon=True)
            t.start()
            _notification_thread = t
    else:
        _notification_stop.set()
    icon.update_menu()


def make_icon():
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(
        [(4, 4), (size - 5, size - 5)],
        radius=12,
        fill=(26, 26, 30, 255),
        outline=(124, 154, 255, 255),
        width=2,
    )
    cx = size // 2
    for i, color in enumerate([(92, 200, 255, 255), (192, 138, 255, 255), (95, 217, 156, 255)]):
        y = cx - 10 + i * 8
        draw.rounded_rectangle(
            [(cx - 14, y), (cx + 14, y + 4)],
            radius=2,
            fill=color,
        )
    return img


# Master PNG icon — used for both the tray (via PIL) and desktop notifications
# (via file path). pystray consumes the PIL image directly; plyer/winotify
# accept the PNG path. A single 256×256 RGBA file works on all platforms.
_ICON_PATH = os.path.join(bundle_root(), "assets", "sport.png")


def _ensure_icon_saved():
    if os.path.exists(_ICON_PATH):
        return _ICON_PATH
    if getattr(sys, "frozen", False):
        return None
    try:
        os.makedirs(os.path.dirname(_ICON_PATH), exist_ok=True)
        # Render at 256x256 for notifications; tray uses the PIL image directly.
        base = make_icon().resize((256, 256), Image.LANCZOS)
        base.save(_ICON_PATH, format="PNG")
        return _ICON_PATH
    except Exception:
        return None


def show_toast(title, msg):
    _notifier.notify(title, msg, icon_path=_ensure_icon_saved() or "")


def notification_loop(stop_event):
    prev_ports = {}
    while not stop_event.is_set():
        if not state["notifications"]:
            stop_event.wait(2.0)
            prev_ports = {}
            continue
        try:
            req = urllib.request.urlopen(f"{DASHBOARD_URL}/api/ports", timeout=2)
            data = json.loads(req.read())
            current = {item["port"]: item.get("process", "?") for item in data["items"]}
            for port, proc in current.items():
                if port not in prev_ports:
                    show_toast(f"端口 {port} 已打开", f"{proc} 正在监听")
            prev_ports = current
        except Exception:
            pass
        stop_event.wait(5.0)


_notification_stop = threading.Event()
_notification_thread = None


def build_menu():
    return pystray.Menu(
        pystray.MenuItem("打开面板", open_dashboard, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(
            "暂停监听" if not state["paused"] else "继续监听",
            toggle_pause,
            checked=lambda item: state["paused"],
        ),
        pystray.MenuItem(
            "开机自启",
            toggle_autostart,
            checked=lambda item: _autostart.is_enabled(),
        ),
        pystray.MenuItem(
            "端口变化通知",
            toggle_notifications,
            checked=lambda item: state["notifications"],
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("退出", quit_app),
    )


def on_ipc_command(command):
    command = (command or "").strip().lower()
    if command == "show":
        open_dashboard()
    elif command == "quit":
        os._exit(0)


def main():
    """Start the IPC server, the tray icon, and the Flask app in the
    background. Blocks until the tray icon exits.
    """
    _instance.start_server(on_ipc_command)

    icon_image = make_icon()
    icon = pystray.Icon(
        "SPort",
        icon_image,
        "SPort — 实时端口监控",
        build_menu(),
    )

    if not SILENT:
        threading.Timer(1.0, open_dashboard).start()

    print(f"  SPort running. Dashboard: {DASHBOARD_URL}")
    print(f"  Right-click tray icon for menu.")

    try:
        icon.run()
    except KeyboardInterrupt:
        pass
    finally:
        _instance.release()


if __name__ == "__main__":
    main()
