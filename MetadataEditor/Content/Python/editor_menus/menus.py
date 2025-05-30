import unreal
import subprocess

def create_tools_menu():
    menu = unreal.ToolMenus.get().find_menu("ContentBrowser.AssetContextMenu")
    menu.add_section("metadata_editor_id", "Metadata Editor")
    new_entry = unreal.ToolMenuEntry(
        name="CustomMenuEntry",
        type=unreal.MultiBlockType.MENU_ENTRY,
        user_interface_action_type=unreal.UserInterfaceActionType.BUTTON
    )
    new_entry.set_label("Edit Metadata")
    new_entry.set_icon("EditorStyle","ContentBrowser.AssetActions.Edit")
    new_entry.set_tool_tip("Opens Metadata Editor Widget")
    new_entry.set_string_command(
        type=unreal.ToolMenuStringCommandType.PYTHON,
        custom_type="",
        string="from editor_menus import metadata_editor; metadata_editor.open_window()"
    )
    menu.add_section("metadata_editor_id", "Metadata Editor")
    menu.add_menu_entry("metadata_editor_id", new_entry)
    unreal.ToolMenus.get().refresh_all_widgets()


def get_unreal_required_packages():
    required_packages = [
        'PySide2==5.15.2.1',
        'PySide6==6.9.0',
        'QtPy==2.4.3',
        'PyAutoGui==0.9.54',
        'pandas==1.3.5',
        'matplotlib==3.9.4'
    ]
    return required_packages

def import_libs(python = "", libs = []):
    print(f"Importing Libs: {python}")
    for lib in libs:
        try:
            cmd = f'{python} -m pip install {lib}'
            subprocess.call(cmd, shell=True)
        except ImportError as e:
            print(f"{e}: Importing Lib: {lib}")
            import_libs(python, {lib})