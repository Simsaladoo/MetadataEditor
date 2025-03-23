import unreal
import sys
import os
from PySide2 import QtUiTools, QtWidgets, QtCore, QtGui

'''
from editor_menus import metadata_editor
from importlib import reload
reload(metadata_editor)
'''



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
        
        
        
def open_window():
    if QtWidgets.QApplication.instance():
        for win in (QtWidgets.QApplication.allWindows()):
            if 'HALONToolShelf' in win.objectName():  # update this name to match name below
                print(f'Destroying previous window...')
                win.destroy()
    else:
        QtWidgets.QApplication(sys.argv)
    MedtadataEditorWidget.window = MedtadataEditorWidget()
    MedtadataEditorWidget.window.show() # show the window
    MedtadataEditorWidget.window.setObjectName('MetadataWidget')  # update this with something unique to your tool
    MedtadataEditorWidget.window.setWindowTitle('Metadata Editor')
    unreal.parent_external_window_to_slate(MedtadataEditorWidget.window.winId(), unreal.SlateParentWindowSearchMethod.MAIN_WINDOW) 
        
        
        

class MedtadataEditorWidget(QtWidgets.QWidget):
    window = None
    def __init__(self, parent=None):
        super(MedtadataEditorWidget, self).__init__(parent)
        widgetPath = f'{os.path.dirname(os.path.abspath(__file__))}/form.ui'
        self.ui = QtUiTools.QUiLoader().load(widgetPath)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.ui)