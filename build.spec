"""PyInstaller spec for SPort.

Cross-platform: produces a single-file executable on Windows/Linux and a
.app bundle (inside a DMG) on macOS.

Build:  pyinstaller build.spec
Output:
  Windows  dist/SPort.exe          (~23 MB)
  macOS    dist/SPort.app/         (~40 MB, onedir bundle)
  Linux    dist/SPort              (~25 MB)
"""
import sys

from PyInstaller.utils.hooks import collect_data_files  # noqa: F401

is_windows = sys.platform == 'win32'
is_macos = sys.platform == 'darwin'
is_linux = not is_windows and not is_macos

block_cipher = None

# --- data files (all platforms) ---------------------------------------------
datas = [
    ('templates', 'templates'),
    ('static',    'static'),
    ('assets',    'assets'),
]

# --- hidden imports — platform-conditional ----------------------------------
hiddenimports = [
    'plyer',
    'plyer.platforms',
]
if is_windows:
    hiddenimports += [
        'winreg',
        'pywintypes',
        'win32api',
        'plyer.platforms.win',
    ]
elif is_macos:
    hiddenimports += [
        'plyer.platforms.macosx',
    ]
else:
    hiddenimports += [
        'plyer.platforms.linux',
    ]

# --- icon -------------------------------------------------------------------
if is_windows:
    icon = 'assets/sport.ico'
else:
    # PyInstaller accepts .png on macOS/Linux
    icon = 'assets/sport.png'

# --- analysis ---------------------------------------------------------------
a = Analysis(
    ['tray.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'tkinter',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# --- executable (onefile on all platforms) -----------------------------------
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SPort',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=is_linux,           # hide console on Windows; on macOS the .app handles it
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon,
)

# --- macOS .app bundle (onedir wrapper around the onefile exe) ---------------
if is_macos:
    app = BUNDLE(
        exe,
        name='SPort.app',
        icon=icon,
        bundle_identifier='com.wanaig.sport',
        info_plist={
            'CFBundleName': 'SPort',
            'CFBundleDisplayName': 'SPort',
            'CFBundleVersion': '0.2.0',
            'CFBundleShortVersionString': '0.2.0',
            'LSBackgroundOnly': False,
            'NSHighResolutionCapable': True,
        },
    )
