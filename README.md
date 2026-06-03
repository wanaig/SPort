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

> **macOS / Linux 开发者**：`pip install` 会自动安装 `plyer`（跨平台通知）和 `pystray`（系统托盘）。macOS 需要 Xcode Command Line Tools；Linux 需要 `libnotify`（`sudo apt install libnotify-dev`）和一个通知守护进程（大多数桌面环境已自带）。`pywin32` 仅 Windows 安装，其它平台自动跳过。

要换端口 / 监听地址（避免端口冲突或允许局域网访问）：

```bash
python tray.py --port 9999 --host 0.0.0.0
# 或
PORT=9999 HOST=0.0.0.0 python tray.py
```

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
- **Windows**：`CreateToolhelp32Snapshot` + `OpenProcess` 获取受保护进程（PPL）信息
- **macOS / Linux**：`psutil` 覆盖所有可见进程，无需额外 API
- 单实例锁：跨平台 TCP localhost 端口（`127.0.0.1:17777`），不依赖系统互斥体
- 自动启动：Windows 注册表 / macOS LaunchAgent / Linux XDG `.desktop`
- 桌面通知：Windows `winotify` / macOS、Linux `plyer`
- 前端为原生 HTML + CSS + JS，无构建步骤，无框架

## 技术栈

- Python 3.10+
- Flask（HTTP 服务 + 静态文件）
- psutil（系统内省）
- pystray + Pillow（系统托盘图标）
- plyer（跨平台桌面通知）
- pywin32（仅 Windows，受保护进程信息）

## 平台支持

| 功能 | Windows | macOS | Linux |
| --- | --- | --- | --- |
| 端口扫描 + 进程信息 | ✅ | ✅ | ✅ |
| 系统托盘图标 | ✅ | ✅ | ✅ |
| 桌面通知 | ✅（winotify） | ✅（plyer/osascript） | ✅（plyer/libnotify） |
| 开机自启 | ✅ 注册表 | ✅ LaunchAgent | ✅ XDG autostart |
| 受保护进程（PPL）信息 | ✅ Toolhelp + OpenProcess | ❌ 不需要 | ❌ 不需要 |
| 预编译安装包 | ✅ exe + 安装器 | ❌ 未实现 | ❌ 未实现 |

## 限制

- **macOS / Linux**：暂无预编译安装包，需从源码运行
- **macOS / Linux**：`sudo` 可查看其他用户的进程信息（`psutil` 在非 root 下只能看到自己的进程）
- **Windows**：PPL 进程（`System`、`MsMpEng.exe` 等）即便管理员也只能看到部分信息
- **Windows SmartScreen**：未签名 exe 首次运行需手动放行

## 项目结构

```
SPort/
├── app.py                  Flask 后端，扫描、终止、详情 API
├── tray.py                 托盘入口（pystray、菜单、单实例协调）
├── platforms/              跨平台适配层
│   ├── __init__.py         平台选择 + 工厂函数
│   ├── _common.py          基类（Autostart、Notifier、SingleInstance、SystemProcessRegistry）
│   ├── windows.py          注册表自启、winotify 通知、Toolhelp PPL 回退
│   ├── darwin.py           LaunchAgent 自启、plyer 通知、macOS 系统进程列表
│   └── linux.py            XDG autostart、plyer 通知、Linux 系统进程列表
├── build.spec              PyInstaller 打包配置
├── installer.iss           Inno Setup 安装脚本
├── build.bat               一键构建：PyInstaller + Inno Setup
├── assets/
│   └── sport.png           应用图标（256×256）
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

`build.bat` 自动在以下位置查找 ISCC.exe（任一即可）：
1. `INNO_SETUP` 环境变量
2. PATH
3. `C:\Program Files (x86)\Inno Setup 6\ISCC.exe`
4. `C:\Program Files\Inno Setup 6\ISCC.exe`
5. `D:\develop\Inno Setup 6\ISCC.exe`
6. `D:\tools\Inno Setup 6\ISCC.exe`

要安装器界面包含中文（EN + 简中），从官方 Unofficial 包下载 `ChineseSimplified.isl` 放到 IS 的 `Languages\` 目录（GitHub Actions 已自动处理；本地首次构建时按提示操作）。

产出：
- `dist/SPort.exe` — 单文件可执行（~23 MB）
- `dist/SPort-Setup-0.2.0.exe` — Windows 安装器（~24 MB）

CI 自动构建：push 到 main 触发验证，push tag `v*` 触发 GitHub Release 上传安装包。

> **macOS / Linux**：暂无自动化构建脚本。从源码运行即可（`python tray.py`）。欢迎贡献 `Makefile` 或平台打包脚本。

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

> **macOS / Linux developers**: `pip install` pulls in `plyer` (cross-platform notifications) and `pystray` (system tray). macOS requires Xcode Command Line Tools; Linux needs `libnotify` (`sudo apt install libnotify-dev`) and a notification daemon (most desktop environments include one). `pywin32` is Windows-only and skipped automatically on other platforms.

For full visibility into protected processes, run as Administrator on Windows or `sudo` on Linux. PPL processes (e.g. `System`, `svchost.exe` under certain protections) may show partial info even with admin rights — that is a Windows security feature, not an app limitation.

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
- **Windows**: `CreateToolhelp32Snapshot` + `OpenProcess` for protected (PPL) process info
- **macOS / Linux**: `psutil` covers all visible processes — no extra API needed
- Single-instance lock: cross-platform TCP localhost socket (`127.0.0.1:17777`), no OS mutex
- Autostart: Windows registry / macOS LaunchAgent / Linux XDG `.desktop`
- Desktop notifications: Windows `winotify`; macOS & Linux `plyer`
- Frontend is vanilla HTML + CSS + JS, no build step, no framework

## Tech stack

- Python 3.10+
- Flask (HTTP server + static files)
- psutil (system introspection)
- pystray + Pillow (system tray icon)
- plyer (cross-platform desktop notifications)
- pywin32 (Windows-only, for protected process info)

## Platform support

| Feature | Windows | macOS | Linux |
| --- | --- | --- | --- |
| Port scan + process info | ✅ | ✅ | ✅ |
| System tray icon | ✅ | ✅ | ✅ |
| Desktop notifications | ✅ (winotify) | ✅ (plyer/osascript) | ✅ (plyer/libnotify) |
| Autostart on login | ✅ Registry | ✅ LaunchAgent | ✅ XDG autostart |
| Protected process (PPL) info | ✅ Toolhelp + OpenProcess | ❌ not needed | ❌ not needed |
| Prebuilt installer | ✅ exe + setup | ❌ not yet | ❌ not yet |

## Limitations

- **macOS / Linux**: no prebuilt binaries — run from source
- **macOS / Linux**: `sudo` may be needed to see other users' processes (`psutil` without root only shows your own)
- **Windows**: PPL processes (`System`, `MsMpEng.exe`, etc.) show partial info even as Administrator
- **Windows SmartScreen**: unsigned exe requires manual approval on first run

## Project layout

```
SPort/
├── app.py                  Flask backend, scan, kill, detail APIs
├── tray.py                 Tray entry (pystray, menu, single-instance)
├── platforms/              Cross-platform adapter layer
│   ├── __init__.py         Platform selection + factory functions
│   ├── _common.py          Base classes (Autostart, Notifier, SingleInstance, SystemProcessRegistry)
│   ├── windows.py          Registry autostart, winotify, Toolhelp PPL fallback
│   ├── darwin.py           LaunchAgent autostart, plyer, macOS system process list
│   └── linux.py            XDG autostart, plyer, Linux system process list
├── build.spec              PyInstaller config
├── installer.iss           Inno Setup script
├── build.bat               One-shot build: PyInstaller + Inno Setup
├── assets/
│   └── sport.png           App icon (256×256)
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

> **macOS / Linux**: no automated build scripts yet. Run from source (`python tray.py`). Contributions for a `Makefile` or platform packaging are welcome.

## API

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/api/ports` | GET | List all listening ports with process context |
| `/api/system-processes` | GET | Built-in system-process and system-account lists |
| `/api/process/<pid>` | GET | Full detail for one process |
| `/api/kill` | POST | Terminate (`{pid, force:false}`) or force-kill (`{pid, force:true}`) |

## License

MIT — see [LICENSE](LICENSE).
