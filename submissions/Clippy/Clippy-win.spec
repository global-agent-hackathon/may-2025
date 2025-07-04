
# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas = [
        ('everything-cli/es.exe', 'everything-cli'),
        ('memory.db', '.'),
        ('storage/', 'storage'),  
        ('src/assets/', 'assets'),  
        ('.env', '.'),
        ('ENV/Lib/site-packages/flet_web/', 'flet_web/web')  # Capital "Lib" for Windows!
    ],    
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Clippy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Clippy',
)
