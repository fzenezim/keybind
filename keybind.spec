"""PyInstaller spec for keybind tray icon executable."""

a = Analysis(
    ['src/keybind/tray.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'keybind',
        'keybind.data_model',
        'keybind.engine',
        'keybind.gui',
        'keybind.core',
        'keybind.tray',
        'pystray',
        'pystray._win32',
        'pynput',
        'pynput.keyboard',
        'pynput.mouse',
        'pyautogui',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'tkinter',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='keybind',
    debug=False,
    strip=False,
    upx=False,
    console=False,
    icon=None,
)
