block_cipher = None

a = Analysis(
    ['Application.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources')
    ],
    hiddenimports=[
        'numpy.core._multiarray_tests',
        'numpy.core._multiarray_umath',
        'app',
        'app.main_window',
        'app.pages',
        'app.pages.add_folder',
        'app.pages.smart_arrange',
        'app.pages.write_exif',
        'app.pages.file_deduplication',
        'app.dialogs',
        'app.dialogs.update_dialog',
        'app.dialogs.UI_UpdateDialog',
        'core',
        'core.common',
        'core.config_manager',
        'threads',
        'threads.smart_arrange_thread',
        'threads.write_exif_thread',
        'threads.file_deduplication_thread',
        'ui',
        'ui.Ui_MainWindow'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LeafSort',
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
    version='LeafSort_version_info.txt',
    icon='resources\\img\\icon.ico',
    optimize=0
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='App'
)
