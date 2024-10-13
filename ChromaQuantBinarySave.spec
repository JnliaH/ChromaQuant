# -*- mode: python ; coding: utf-8 -*-

added_files = [
	( 'AutoFpmMatch.py' , '.' ),
	( 'AutoQuantification.py' , '.'),
	( 'handleDirectories.py', './_internal' ),
	( 'duplicateMatch.py' , '.' ),
	( 'README.md' , '.' ),
	( 'LICENSE.txt' , '.' ),
	( 'LICENSES_bundled.txt' , '.' ),
]
	
a = Analysis(
    ['QuantUI.py'],
    pathex=[],
    binaries=[],
    datas=[],
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
    name='ChromaQuant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['ChromaQuantIcon.icns'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ChromaQuantBinary',
)
