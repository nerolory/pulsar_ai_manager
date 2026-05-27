# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for PulsarAI backend
# Build: pyinstaller pulsar_backend.spec
# Output: dist/pulsar_backend/pulsar_backend.exe

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        # uvicorn internals
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.loops.asyncio',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.http.httptools_impl',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.protocols.websockets.websockets_impl',
        'uvicorn.protocols.websockets.wsproto_impl',
        'uvicorn.lifespan',
        'uvicorn.lifespan.off',
        'uvicorn.lifespan.on',
        # fastapi / starlette
        'fastapi',
        'starlette',
        'starlette.routing',
        'starlette.middleware.cors',
        # pydantic
        'pydantic',
        'pydantic.v1',
        'pydantic_settings',
        # app providers (lazy imports in routes/settings.py)
        'app.providers.mock',
        'app.providers.openrouter',
        'app.providers.vsellm',
        # stdlib
        'email.mime.multipart',
        'email.mime.text',
        'asyncio',
        'sqlite3',
        'yaml',
        'aiosqlite',
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
    name='pulsar_backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,   # keep console for logging; Electron will spawn it hidden
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='pulsar_backend',
)
