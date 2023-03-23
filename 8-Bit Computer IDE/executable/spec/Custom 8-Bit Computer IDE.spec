# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['C:\\Users\\ABI\\Desktop\\8-Bit Computer IDE Project\\8-Bit Computer IDE\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\ABI\\Desktop\\8-Bit Computer IDE Project\\8-Bit Computer IDE\\externals', '.')],
    hiddenimports=[],
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
    name='Custom 8-Bit Computer IDE',
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
    icon=['C:\\Users\\ABI\\Desktop\\8-Bit Computer IDE Project\\8-Bit Computer IDE\\externals\\icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Custom 8-Bit Computer IDE',
)
