# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['main.py'],
             pathex=['D', '/Users/danieljiang/Documents/UMTRI_3D_Scan_Processing/venv/lib/python3.9/site-packages', '/Users/danieljiang/Documents/UMTRI_3D_Scan_Processing'],
             binaries=[],
             datas=[],
             hiddenimports=['vtkmodules','vtkmodules.all','vtkmodules.qt'],
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
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )

app = BUNDLE(exe,
         name='Simba.app',
         icon='Simba.ico',
         bundle_identifier=None,
	version = '1.0.0')
