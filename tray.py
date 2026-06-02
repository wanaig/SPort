"""SPort tray entry point.

Starts Flask in a background thread and shows a pystray icon for control.
Single-instance: a second launch forwards a 'show' command to the running one
and exits.
"""
import os
import sys
import time
import threading
import webbrowser
import atexit
import urllib.request

from app import app
from singleinstance import SingleInstance
from autostart import is_enabled as autostart_is_enabled, set_enabled as autostart_set_enabled

import pystray
from PIL import Image, ImageDraw

PORT = int(os.environ.get("PORT", 7777))
HOST = os.environ.get("HOST", "127.0.0.1")
SILENT = "--silent" in sys.argv
DASHBOARD_URL = f"http://{HOST}:{PORT}"

_instance = SingleInstance("SPort")
atexit.register(_instance.release)

if not _instance.is_first:
    _instance.send_command("show")
    print("SPort is already running. Opening dashboard in browser...")
    sys.exit(0)

state = {
    "paused": False,
    "notifications": False,
}


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
    new = not autostart_is_enabled()
    autostart_set_enabled(new)
    icon.update_menu()


def toggle_notifications(icon, item):
    state["notifications"] = not state["notifications"]
    app.config["SPORT_NOTIFY"] = state["notifications"]
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
            checked=lambda item: autostart_is_enabled(),
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
