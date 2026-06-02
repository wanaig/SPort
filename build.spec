"""PyInstaller spec for SPort.

Build: pyinstaller build.spec
Output: dist/SPort.exe
"""
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

datas = [
    ('templates', 'templates'),
    ('static', 'static'),
    ('assets', 'assets'),
]

hiddenimports = [
    'win32event',
    'win32pipe',
    'win32file',
    'win32api',
    'winerror',
    'winotify',
    'winotify.audio',
]

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
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/sport.ico',
)
