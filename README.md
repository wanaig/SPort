# SPort

Real-time Windows port monitor for microservice developers. See which process owns every listening port, kill conflicting services in one click, and filter out Windows system noise so you only see what matters.

## Why

When you run a dozen microservices locally, port conflicts (`EADDRINUSE`) are constant. `netstat -ano` works but is a wall of text mixing your dev stack with hundreds of Windows system ports. SPort gives you a live dashboard with full process context, sorted and filtered, with kill buttons.

## Features

- **Live scan** with 2s default refresh (1s / 2s / 5s / 10s selectable)
- **Process detail modal** — PID, status, user, memory, CPU, started, cwd, command line, executable path
- **Partial-info support** for Windows kernel-protected (PPL) processes — shows what is available, explains what is not
- **Hide-system toggle** — filters out 35+ known system processes and 6 system accounts (svchost, lsass, services, NT AUTHORITY\SYSTEM, etc.)
- **Custom filter list** — add your own noise (e.g. `vmware-authd.exe`); stored in browser localStorage
- **Common-port tags** — auto-labels 19 well-known services (MySQL 3306, Redis 6379, Postgres 5432, etc.)
- **Multi-port detection** — flags processes that own several ports
- **Search, sort, filter** — by port, PID, process name, address; filter by protocol or category
- **One-click terminate** with confirm; force-kill escalation
- **Bilingual UI** — 中文 / English, persisted per browser
- **Local-only** — no telemetry, no network calls, no data leaves the machine

## Quick start

```bash
git clone https://github.com/wanaig/SPort.git
cd SPort
pip install -r requirements.txt
python app.py
```

Or on Windows, double-click `start.bat` (handles pip install + launch).

Then open <http://127.0.0.1:7777>.

For full visibility into protected processes, run as Administrator. PPL processes (e.g. `System`, `svchost.exe` under certain protections) may show partial info even with admin rights — that is a Windows security feature, not an app limitation.

## Keyboard shortcuts

| Key | Action |
| --- | --- |
| `/` | Focus search |
| `R` | Refresh now |
| `Space` | Pause / resume auto-refresh |
| `Esc` | Close modal / clear search |

## How it works

- `psutil.net_connections('inet')` for socket-to-PID mapping
- `psutil.Process(pid)` for memory, CPU, owner, command line
- `CreateToolhelp32Snapshot` (Windows Toolhelp API) for process names when psutil access is denied
- `OpenProcess` with `PROCESS_QUERY_LIMITED_INFORMATION` for executable paths of protected processes
- Frontend is vanilla HTML + CSS + JS, no build step, no framework

## Tech stack

- Python 3.10+
- Flask (HTTP server + static files)
- psutil (system introspection)
- pywin32 (Windows API for protected process info)

## Project layout

```
SPort/
├── app.py                  Flask backend, scan, kill, detail APIs
├── requirements.txt
├── start.bat               Windows one-click launcher
├── templates/
│   └── index.html          Dashboard markup
└── static/
    ├── style.css           Dark theme
    └── app.js              I18n, render, modal, filter logic
```

## API

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/api/ports` | GET | List all listening ports with process context |
| `/api/system-processes` | GET | Built-in system-process and system-account lists |
| `/api/process/<pid>` | GET | Full detail for one process |
| `/api/kill` | POST | Terminate (`{pid, force:false}`) or force-kill (`{pid, force:true}`) |

## License

MIT — see [LICENSE](LICENSE).
