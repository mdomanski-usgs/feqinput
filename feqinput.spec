# -*- mode: python -*-

block_cipher = None


a = Analysis(['feqinput.py'],
             pathex=['.'],
             binaries=[('feq_1061.exe', '.'), ('fequtl.exe', '.'), ('FEQ-GDI.jar','.')],
             datas=[('usermanual.pdf','.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='feqinput',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon=r'.\images\resources\icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='feqinput')
