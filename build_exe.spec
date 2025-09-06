# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Ana uygulama için analiz
a = Analysis(
    ['main.py'],
    pathex=['d:\\Belgelerim\\Python Projects\\DPI_Program'],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('external', 'external'),
        ('src', 'src'),
        ('logs', 'logs'),
        ('README.md', '.'),
        ('LICENSE', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'colorama',
        'pystray',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'threading',
        'subprocess',
        'psutil',
        'yaml',
        'requests',
        'scapy',
        'pywin32',
        'win32api',
        'win32con',
        'win32gui',
        'src.config_manager',
        'src.dpi_bypass',
        'src.goodbyedpi_wrapper',
        'src.zapret_wrapper',
        'src.ui.console_ui',
        'src.ui.gui',
        'src.ui.modern_gui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='NetLanGuardian',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Console açık olsun ki log mesajları görülebilsin
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # İcon dosyanız varsa buraya ekleyin
    uac_admin=True,  # Yönetici hakları iste
    uac_uiaccess=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NetLanGuardian',
)
