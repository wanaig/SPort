# SPort

面向微服务开发者的 Windows 实时端口监控工具。查看每个监听端口的所属进程，一键结束冲突服务，过滤 Windows 系统噪音端口，只看你关心的内容。

## 为什么

本地跑十几个微服务时，端口冲突（`EADDRINUSE`）家常便饭。`netstat -ano` 也能用，但满屏文字把开发栈和数百个 Windows 系统端口混在一起。SPort 提供实时面板，带完整进程上下文，支持排序、过滤，一键结束。

## 功能

- **实时扫描** — 默认 2 秒刷新（可选 1s / 2s / 5s / 10s）
- **进程详情弹窗** — PID、状态、用户、内存、CPU、启动时间、工作目录、命令行、可执行文件路径
- **Windows 内核保护进程（PPL）部分信息支持** — 显示可获取的信息，并说明受限字段
- **隐藏系统端口开关** — 过滤 35+ 已知系统进程和 6 个系统账户（svchost、lsass、services、NT AUTHORITY\SYSTEM 等）
- **自定义过滤列表** — 浏览器 localStorage 存储你添加的噪音进程（如 `vmware-authd.exe`）
- **常用端口标签** — 自动标记 19 个常见服务（MySQL 3306、Redis 6379、Postgres 5432 等）
- **多端口检测** — 标记占用多个端口的进程
- **搜索、排序、过滤** — 按端口、PID、进程名、地址筛选；按协议或类别过滤
- **一键终止**带确认；可升级为强制结束
- **中英双语界面** — 浏览器中持久化
- **完全本地运行** — 无遥测、无网络请求、数据不离开本机

## 安装

下载适合你系统的版本，双击运行。

| 形式 | 体积 | 说明 |
| --- | --- | --- |
| **SPort-Setup-x.x.x.exe**（推荐） | ~12 MB | 标准 Windows 安装器，可从"应用和功能"卸载；安装到 `%LOCALAPPDATA%\SPort\`；可选桌面快捷方式、开机自启 |
| **SPort.exe**（便携） | ~23 MB | 单文件，丢到任意目录双击即可；无注册表项、无卸载入口 |

从 [Releases](https://github.com/wanaig/SPort/releases) 下载。

**首次运行**：Windows SmartScreen 会弹"Windows protected your PC"。点 **更多信息** → **仍要运行** 即可（项目未做代码签名）。

**首次启动行为**：
- 任务栏右下角出现 SPort 图标
- 默认浏览器自动打开 <http://127.0.0.1:7777>（安装版可在安装时取消勾选"启动 SPort"避免自动开浏览器）
- 右键托盘图标：打开面板 / 暂停 / 开机自启 / 端口通知 / 退出

**再次启动**：从开始菜单 / 桌面 / 文件管理器双击即可。已在后台运行时再次启动会唤起浏览器，不会重复开服务器。

## 快速开始（从源码运行）

不下载预编译包，直接从源码跑：

```bash
git clone https://github.com/wanaig/SPort.git
cd SPort
pip install -r requirements.txt
python tray.py          # 带托盘；或 python app.py 只跑 Flask
```

随后访问 <http://127.0.0.1:7777>。

要完整查看受保护进程，建议以管理员身份运行。PPL 进程（如 `System`、部分受保护的 `svchost.exe`）即便管理员权限也只能看到部分信息 —— 这是 Windows 的安全机制，不是 SPort 的限制。

## 键盘快捷键

| 键 | 操作 |
| --- | --- |
| `/` | 聚焦搜索框 |
| `R` | 立即刷新 |
| `Space` | 暂停 / 继续自动刷新 |
| `Esc` | 关闭弹窗 / 清除搜索 |

## 工作原理

- `psutil.net_connections('inet')` — socket 与 PID 映射
- `psutil.Process(pid)` — 内存、CPU、所有者、命令行
- `CreateToolhelp32Snapshot`（Windows Toolhelp API）— psutil 访问被拒时获取进程名
- `OpenProcess` + `PROCESS_QUERY_LIMITED_INFORMATION` — 受保护进程的可执行文件路径
- 前端为原生 HTML + CSS + JS，无构建步骤，无框架

## 技术栈

- Python 3.10+
- Flask（HTTP 服务 + 静态文件）
- psutil（系统内省）
- pywin32（Windows API，受保护进程信息）

## 项目结构

```
SPort/
├── app.py                  Flask 后端，扫描、终止、详情 API
├── tray.py                 托盘入口（pystray、菜单、单实例协调）
├── singleinstance.py       Windows 命名互斥体 + 命名管道
├── autostart.py            注册表 Run 项读写
├── build.spec              PyInstaller 打包配置
├── installer.iss           Inno Setup 安装脚本
├── build.bat               一键构建：PyInstaller + Inno Setup
├── assets/
│   └── sport.ico           多尺寸应用图标
├── requirements.txt
├── start.bat               Windows 一键启动（开发用）
├── templates/
│   └── index.html          面板结构
└── static/
    ├── style.css           深色主题
    └── app.js              i18n、渲染、弹窗、过滤逻辑
```

## 构建

```bash
pip install pyinstaller            # + Inno Setup 6（从 jrsoftware.org 下载）
python -m pip install -r requirements.txt
build.bat
```

产出：
- `dist/SPort.exe` — 单文件可执行（~23 MB）
- `dist/SPort-Setup-0.2.0.exe` — Windows 安装器（~12 MB）

## API

| 端点 | 方法 | 用途 |
| --- | --- | --- |
| `/api/ports` | GET | 列出所有监听端口及进程上下文 |
| `/api/system-processes` | GET | 内置系统进程和系统账户列表 |
| `/api/process/<pid>` | GET | 单个进程的完整详情 |
| `/api/kill` | POST | 终止（`{pid, force:false}`）或强制结束（`{pid, force:true}`） |

## 许可证

MIT — 见 [LICENSE](LICENSE)。

---

## English

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

## Install

Download a prebuilt release, or run from source.

| Distribution | Size | Notes |
| --- | --- | --- |
| **SPort-Setup-x.x.x.exe** (recommended) | ~12 MB | Standard Windows installer; uninstallable via Settings → Apps; installs to `%LOCALAPPDATA%\SPort\`; optional desktop shortcut and autostart |
| **SPort.exe** (portable) | ~23 MB | Single file, drop anywhere and run; no registry entries, no uninstaller |

Download from [Releases](https://github.com/wanaig/SPort/releases).

**First run**: Windows SmartScreen may show "Windows protected your PC". Click **More info** → **Run anyway** (the project is not code-signed).

**After launch**:
- SPort icon appears in the system tray
- Default browser opens <http://127.0.0.1:7777>
- Right-click the tray icon: open dashboard, pause, autostart, port notifications, quit

**Subsequent launches**: a second launch wakes the running instance's browser instead of starting a duplicate server.

## Quick start (from source)

```bash
git clone https://github.com/wanaig/SPort.git
cd SPort
pip install -r requirements.txt
python tray.py          # tray + Flask; or python app.py for Flask only
```

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
├── tray.py                 Tray entry (pystray, menu, single-instance)
├── singleinstance.py       Windows named mutex + named pipe
├── autostart.py            Registry Run key read/write
├── build.spec              PyInstaller config
├── installer.iss           Inno Setup script
├── build.bat               One-shot build: PyInstaller + Inno Setup
├── assets/
│   └── sport.ico           Multi-resolution app icon
├── requirements.txt
├── start.bat               Windows one-click launcher (dev)
├── templates/
│   └── index.html          Dashboard markup
└── static/
    ├── style.css           Dark theme
    └── app.js              I18n, render, modal, filter logic
```

## Building

```bash
pip install pyinstaller            # + Inno Setup 6 from jrsoftware.org
python -m pip install -r requirements.txt
build.bat
```

Outputs:
- `dist/SPort.exe` — single-file executable (~23 MB)
- `dist/SPort-Setup-0.2.0.exe` — Windows installer (~12 MB)

## API

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/api/ports` | GET | List all listening ports with process context |
| `/api/system-processes` | GET | Built-in system-process and system-account lists |
| `/api/process/<pid>` | GET | Full detail for one process |
| `/api/kill` | POST | Terminate (`{pid, force:false}`) or force-kill (`{pid, force:true}`) |

## License

MIT — see [LICENSE](LICENSE).
