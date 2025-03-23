import unreal

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
    