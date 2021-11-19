# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['DeMainUI.py', 'DeBackup.py', 'DeBackupHandler.py', 'DeWorker.py',
              'DeSettingsManager.py'],
             pathex=[],
             binaries=[],
             datas=[('./assets/icon24.png', 'assets'), ('./assets/device_icons/*', 'assets/device_icons/')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='DeTuner',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='DeTuner')
