import unreal
import os
import sys
import subprocess

python_executable = f"{unreal.Paths().engine_dir()}/Binaries/ThirdParty/Python3/Win64/python.exe"
saved_lib_path  = f"{unreal.Paths.project_saved_dir()}/site-packages"
if not os.path.exists(saved_lib_path):
    os.mkdir(saved_lib_path)
sys.path.insert(0, saved_lib_path)
try:
    import qtpy
    # import qdarkstyle
    print(f"qtpy imported")

except ImportError as e:
    print(f"Import Error!: {e}")
    for package in required_packages:
        cmd = f"{python_executable} -m pip install {package} --target={saved_lib_path}"
        print(cmd)
        subprocess.run(cmd, shell=True)

from editor_menus import menus
menus.create_tools_menu()
