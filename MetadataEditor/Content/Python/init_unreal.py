import unreal
import sys
import pathlib
import subprocess
import shlex
from editor_menus import menus

package_string = ' '.join(menus.get_unreal_required_packages())
saved_path = pathlib.Path(unreal.Paths().project_saved_dir())
engine_path = pathlib.Path(unreal.Paths().engine_dir())
python_executable = engine_path / "Binaries/ThirdParty/Python3/Win64/python.exe"
saved_lib_path = saved_path / 'site-packages'
saved_lib_path.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, saved_lib_path.as_posix())
cmd = f'"{python_executable.resolve().as_posix()}" -m pip install {package_string} --target="{saved_lib_path.as_posix()}"'

try:
    import qtpy
    print(f"qtpy imported!")
    menus.create_tools_menu()
except ImportError as e:
    print(f"Import Error!: {e}")
    subprocess.call(shlex.split(cmd), shell=True)



