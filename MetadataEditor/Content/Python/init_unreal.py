import unreal
import os
import sys
import pathlib
import subprocess
import shlex

required_packages = [
    'PySide2==5.15.2.1',
    'QtPy==2.4.1'
]
package_string = ' '.join(required_packages)
saved_path = pathlib.Path(unreal.Paths().project_saved_dir())
engine_path = pathlib.Path(unreal.Paths().engine_dir())
python_executable = engine_path / "Binaries/ThirdParty/Python3/Win64/python.exe"

saved_lib_path = saved_path / 'site-packages'
saved_lib_path.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, saved_lib_path.as_posix())

cmd = f'"{python_executable.resolve().as_posix()}" -m pip install {package_string} --target="{saved_lib_path.as_posix()}"'
try:
    import qtpy
    print(f"qtpy imported")

except ImportError as e:
    print(f"Import Error!: {e}")
    subprocess.call(shlex.split(cmd), shell=True)

from editor_menus import menus
menus.create_tools_menu()
