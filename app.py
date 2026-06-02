"""SPort - Real-time port monitor for microservice developers."""
import os
import sys
import time
import ctypes
import socket
from ctypes import wintypes
from datetime import datetime
from flask import Flask, jsonify, request, render_template

try:
    import psutil
except ImportError:
    print("Missing dependency 'psutil'. Run: pip install -r requirements.txt")
    sys.exit(1)

IS_WINDOWS = sys.platform == "win32"
if IS_WINDOWS:
    try:
        _kernel32 = ctypes.windll.kernel32
    except Exception:
        IS_WINDOWS = False

app = Flask(__name__)

COMMON_PORTS = {
    80: "HTTP", 443: "HTTPS", 3000: "React/Node", 3306: "MySQL",
    4000: "Node alt", 5000: "Flask/Python", 5173: "Vite", 5432: "PostgreSQL",
    6379: "Redis", 8000: "Django/FastAPI", 8080: "HTTP alt", 8443: "HTTPS alt",
    9000: "PHP-FPM", 9090: "Prometheus", 9200: "Elasticsearch",
    27017: "MongoDB", 28017: "MongoDB Web", 50000: "SAP", 33060: "MySQL X",
}

KILL_BLOCKLIST = {
    0, 4, 8, 120, 144, 172, 240, 304, 328, 336, 472, 560, 640, 664,
    700, 724, 808, 856, 944, 1064, 1100, 1204, 1240, 1264, 1324,
    1336, 1384, 1464, 1492, 1524, 1608, 1644, 1660, 1684, 1776,
    1784, 1824, 1852, 1888, 1900, 1932, 1960, 1984, 2000, 2024,
}

# Built-in Windows system processes (matched case-insensitive, .exe suffix ignored)
SYSTEM_PROCESSES = {
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

SYSTEM_USERS = {
    "NT AUTHORITY\\SYSTEM",
    "NT AUTHORITY\\LOCAL SERVICE",
    "NT AUTHORITY\\NETWORK SERVICE",
    "SYSTEM", "LOCAL SERVICE", "NETWORK SERVICE",
}

# Toolhelp snapshot cache for protected process names
_TOOLHELP_CACHE = {"data": {}, "ts": 0.0}
_TOOLHELP_TTL = 15.0


# =====================================================================
# Windows API helpers for protected processes (PPL/AntiMalware)
# =====================================================================
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


def _refresh_toolhelp():
    """Snapshot of {pid: process_name} using Toolhelp32. Works for PPL/AntiMalware."""
    now = time.time()
    if _TOOLHELP_CACHE["data"] and (now - _TOOLHELP_CACHE["ts"]) < _TOOLHELP_TTL:
        return _TOOLHELP_CACHE["data"]

    data = {}
    if IS_WINDOWS:
        try:
            TH32CS_SNAPPROCESS = 0x00000002
            PE32W = _build_pe32w()
            snapshot = _kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
            if snapshot and snapshot != -1:
                try:
                    entry = PE32W()
                    entry.dwSize = ctypes.sizeof(entry)
                    if _kernel32.Process32FirstW(snapshot, ctypes.byref(entry)):
                        while True:
                            data[entry.th32ProcessID] = entry.szExeFile
                            if not _kernel32.Process32NextW(snapshot, ctypes.byref(entry)):
                                break
                finally:
                    _kernel32.CloseHandle(snapshot)
        except Exception:
            pass

    _TOOLHELP_CACHE["data"] = data
    _TOOLHELP_CACHE["ts"] = now
    return data


def _get_exe_limited(pid):
    """Get full exe path with PROCESS_QUERY_LIMITED_INFORMATION. Works for some PPL."""
    if not IS_WINDOWS or not pid:
        return None
    try:
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = _kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return None
        try:
            buf = ctypes.create_unicode_buffer(1024)
            size = wintypes.DWORD(1024)
            if _kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
                return buf.value
        finally:
            _kernel32.CloseHandle(handle)
    except Exception:
        return None


def get_process_info(pid):
    """Get process info with multi-level fallback:
    1. psutil (full info)
    2. Toolhelp snapshot (name only, works for PPL)
    3. Empty fallback
    """
    if not pid:
        return {"name": "System", "exe": "", "username": "\u2014", "partial": False}

    try:
        p = psutil.Process(pid)
        with p.oneshot():
            return {
                "name": p.name(),
                "exe": p.exe() if hasattr(p, "exe") else "",
                "username": p.username() if hasattr(p, "username") else "",
                "create_time": p.create_time(),
                "partial": False,
            }
    except (psutil.NoSuchProcess, psutil.ZombieProcess):
        return {"name": f"(pid {pid})", "exe": "", "username": "?", "partial": False}
    except psutil.AccessDenied:
        name = _refresh_toolhelp().get(pid)
        exe = _get_exe_limited(pid) or ""
        return {
            "name": name or f"(pid {pid})",
            "exe": exe,
            "username": "?",
            "create_time": 0,
            "partial": True,
        }


def _is_system_process(process_name, username):
    """Decide if a row represents a Windows system service.
    Matches against the built-in process name set and well-known system accounts.
    """
    if not process_name:
        return False
    proc_lc = process_name.lower()
    if proc_lc in SYSTEM_PROCESSES:
        return True
    # Strip .exe for matching
    base = proc_lc[:-4] if proc_lc.endswith(".exe") else proc_lc
    for sp in SYSTEM_PROCESSES:
        sp_lc = sp.lower()
        sp_base = sp_lc[:-4] if sp_lc.endswith(".exe") else sp_lc
        if base == sp_base:
            return True
    if username and username.upper() in {u.upper() for u in SYSTEM_USERS}:
        return True
    return False


_last_scan_cache = {"data": None}


def scan_ports():
    """Scan all listening TCP/UDP ports with their owning process.

    When app.config['SPORT_PAUSED'] is True, returns the most recent
    successful scan (with summary.paused = True) instead of rescanning.
    """
    if app.config.get("SPORT_PAUSED", False) and _last_scan_cache["data"] is not None:
        cached = _last_scan_cache["data"]
        return {
            **cached,
            "summary": {**cached["summary"], "paused": True},
        }

    results = []
    seen = set()
    try:
        connections = psutil.net_connections(kind="inet")
    except (psutil.AccessDenied, OSError) as e:
        return {"error": str(e), "items": []}

    for conn in connections:
        if conn.status != psutil.CONN_LISTEN:
            continue
        if not conn.laddr:
            continue

        key = (conn.laddr.ip, conn.laddr.port, conn.pid, conn.type)
        if key in seen:
            continue
        seen.add(key)

        info = get_process_info(conn.pid)
        port = conn.laddr.port
        is_common = port in COMMON_PORTS
        is_blocked = port in KILL_BLOCKLIST or conn.pid in (0, 4)
        is_system = _is_system_process(info["name"], info["username"])

        results.append({
            "protocol": "TCP" if conn.type == socket.SOCK_STREAM else "UDP",
            "address": conn.laddr.ip,
            "port": port,
            "pid": conn.pid,
            "process": info["name"],
            "username": info["username"],
            "exe": info["exe"],
            "common": COMMON_PORTS.get(port, ""),
            "is_blocked": is_blocked,
            "is_system": is_system,
        })

    results.sort(key=lambda x: (x["port"], x["pid"] or 0))

    by_port = {}
    by_pid = {}
    for r in results:
        by_port[r["port"]] = by_port.get(r["port"], 0) + 1
        by_pid[r["pid"]] = by_pid.get(r["pid"], 0) + 1

    duplicates = {pid: cnt for pid, cnt in by_pid.items() if cnt > 1}
    hidden_count = sum(1 for r in results if r["is_system"])

    result = {
        "items": results,
        "summary": {
            "total": len(results),
            "tcp": sum(1 for r in results if r["protocol"] == "TCP"),
            "udp": sum(1 for r in results if r["protocol"] == "UDP"),
            "unique_ports": len(by_port),
            "duplicate_pids": len(duplicates),
            "processes": len(set(r["pid"] for r in results if r["pid"])),
            "hidden": hidden_count,
            "scanned_at": datetime.now().isoformat(timespec="seconds"),
            "paused": False,
        },
        "duplicates": duplicates,
    }
    _last_scan_cache["data"] = result
    return result


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/ports")
def api_ports():
    return jsonify(scan_ports())


@app.route("/api/system-processes")
def api_system_processes():
    return jsonify({
        "builtin": sorted(SYSTEM_PROCESSES),
        "users": sorted(SYSTEM_USERS),
    })


@app.route("/api/kill", methods=["POST"])
def api_kill():
    data = request.get_json(silent=True) or {}
    pid = data.get("pid")
    force = bool(data.get("force"))

    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "Invalid pid"}), 400

    if pid <= 0:
        return jsonify({"ok": False, "error": "Refusing to kill system pid"}), 403

    try:
        p = psutil.Process(pid)
        info = {"name": p.name(), "pid": pid}
        if force:
            p.kill()
        else:
            p.terminate()
        return jsonify({"ok": True, "action": "kill" if force else "terminate", **info})
    except psutil.NoSuchProcess:
        return jsonify({"ok": False, "error": "Process not found"}), 404
    except psutil.AccessDenied:
        return jsonify({"ok": False, "error": "Access denied (try run as Administrator)"}), 403
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/process/<int:pid>")
def api_process(pid):
    try:
        p = psutil.Process(pid)
        with p.oneshot():
            return jsonify({
                "pid": pid,
                "name": p.name(),
                "exe": p.exe() if hasattr(p, "exe") else "",
                "cmdline": p.cmdline() if hasattr(p, "cmdline") else [],
                "cwd": p.cwd() if hasattr(p, "cwd") else "",
                "username": p.username() if hasattr(p, "username") else "",
                "create_time": p.create_time(),
                "status": p.status(),
                "memory_mb": round(p.memory_info().rss / 1024 / 1024, 1) if p.memory_info() else 0,
                "cpu_percent": p.cpu_percent(interval=0.1),
                "partial": False,
            })
    except psutil.NoSuchProcess:
        return jsonify({"error": "not found", "message": "Process no longer exists"}), 404
    except psutil.AccessDenied:
        name = _refresh_toolhelp().get(pid)
        exe = _get_exe_limited(pid)
        if not name and not exe:
            return jsonify({
                "error": "access denied",
                "message": "Kernel-protected process; no details available.",
            }), 403
        return jsonify({
            "pid": pid,
            "name": name or f"(pid {pid})",
            "exe": exe or "",
            "cmdline": [],
            "cwd": "",
            "username": "",
            "create_time": 0,
            "status": "protected",
            "memory_mb": 0,
            "cpu_percent": 0,
            "partial": True,
        })


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7777))
    host = os.environ.get("HOST", "127.0.0.1")
    print("\n  SPort — Real-time port monitor")
    print(f"  ─────────────────────────────────────────")
    print(f"  Local:    http://{host}:{port}")
    print(f"  Network:  http://{get_local_ip()}:{port}")
    print(f"  Press Ctrl+C to stop\n")
    app.run(host=host, port=port, debug=False, threaded=True)
