import unreal
import sys
import os
from PySide2 import QtUiTools, QtWidgets, QtCore, QtGui

'''
from editor_menus import metadata_editor
from importlib import reload
reload(metadata_editor)
metadata_editor.open_window()
'''

def save_asset():
    print(f"Saved!")
    return


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
        
        
def open_window():
    selected = get_selected_assets()
    if not len(selected) > 0:
        return
    if QtWidgets.QApplication.instance():
        for win in (QtWidgets.QApplication.allWindows()):
            if 'Metadata' in win.objectName():  # update this name to match name below
                print(f'Destroying previous window...')
                win.destroy()
    else:
        QtWidgets.QApplication(sys.argv)
    MetadataEditorWidget.window = MetadataEditorWidget()
    MetadataEditorWidget.window.show() # show the window
    MetadataEditorWidget.window.setObjectName('MetadataEditorWidget')  # update this with something unique to your tool
    MetadataEditorWidget.window.setWindowTitle('Metadata Editor')
    unreal.parent_external_window_to_slate(MetadataEditorWidget.window.winId(), unreal.SlateParentWindowSearchMethod.MAIN_WINDOW) 
  
        

class MetadataEditorWidget(QtWidgets.QWidget):
    window = None
    def __init__(self, parent=None):
        super(MetadataEditorWidget, self).__init__(parent)
        widgetPath = f'{os.path.dirname(os.path.abspath(__file__))}/form.ui'
        self.ui = QtUiTools.QUiLoader().load(widgetPath)
        layout = QtWidgets.QVBoxLayout(self)
        self.ui.setLayout(layout)
        self.ui.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)
        ## self.ui.setWindowIcon(QtGui.QIcon(f"stroked.png"))
        layout.setMargin(0)
        layout.addWidget(self.ui)
        self.ui.pushButton_Save = self.ui.findChild(QtWidgets.QPushButton, 'pushButton_Save')
        self.ui.pushButton_Save.clicked.connect(save_asset)
        
        ## Here we need to get all the selecteds
        selected = get_selected_assets()
        # If we are going to allow for multi-edit -- we'll need to expand the window

        
        existing_tags = get_asset_metadata(get_selected_assets()[0])