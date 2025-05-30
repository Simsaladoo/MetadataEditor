import unreal
import sys
from editor_menus import ui
from PySide2 import QtWidgets

'''
from editor_menus import metadata_editor
from importlib import reload
reload(metadata_editor)
metadata_editor.open_window()
'''
app = None

def get_add_row_style():
    green_button_hover_style = """
        QPushButton {background-color: rgb(30,55,44);color: white;}
        QPushButton::hover {background-color: rgb(60,110,88);color: white;}
        QLabel {color: rgb(30,55,44);color: white;}  
        """
    return green_button_hover_style

def get_selected_assets():
    editor_util = unreal.EditorUtilityLibrary()
    selected_assets = editor_util.get_selected_assets()
    if not selected_assets:
        print("No assets selected.")
        return []
    asset_paths = [asset.get_path_name() for asset in selected_assets]
    return asset_paths


def set_metadata_on_asset(asset_path, key, value):
    asset = unreal.EditorAssetLibrary.load_asset(asset_path)
    if asset:
        unreal.EditorAssetLibrary.set_metadata_tag(asset, key, value)
        print(f"Metadata set: {key} -> {value} on {asset_path}")
    else:
        print(f"Failed to load asset: {asset_path}")
        
    
def get_asset_metadata(asset_path):
    asset = unreal.EditorAssetLibrary.load_asset(asset_path)
    if not asset:
        print(f"Failed to load asset: {asset_path}")
        return {}
    metadata_dict = unreal.EditorAssetLibrary.get_metadata_tag_values(asset)
    if metadata_dict:
        print(f"Metadata for {asset_path}: {metadata_dict}")
    else:
        print(f"No metadata found for {asset_path}")
    return metadata_dict
        

  

        
