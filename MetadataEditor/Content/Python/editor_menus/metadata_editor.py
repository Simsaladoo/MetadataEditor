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
    MetadataEditorWidget.window.resize(300,150)
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))) + "/Resources/Icon128.png"
    MetadataEditorWidget.window.setWindowIcon(QtGui.QIcon(path))
    unreal.parent_external_window_to_slate(MetadataEditorWidget.window.winId(), unreal.SlateParentWindowSearchMethod.MAIN_WINDOW) 
  
  
def get_add_row_style():
    green_button_hover_style = """
        QPushButton {background-color: rgb(30,55,44);color: white;}
        QPushButton::hover {background-color: rgb(60,110,88);color: white;}
        QLabel {color: rgb(30,55,44);color: white;}  
        """
    return green_button_hover_style
        

class MetadataEditorWidget(QtWidgets.QWidget):
    window = None
    def __init__(self, parent=None):
        super(MetadataEditorWidget, self).__init__(parent)
        widgetPath = f'{os.path.dirname(os.path.abspath(__file__))}/form.ui'
        self.ui = QtUiTools.QUiLoader().load(widgetPath)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setMargin(0)
        self.ui.setLayout(layout)
        self.ui.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)
        ## self.ui.setWindowIcon(QtGui.QIcon(f"stroked.png"))
        layout.addWidget(self.ui)        
        self.init_ui()
        

        
    def init_ui(self):
        # self.ui.verticalLayout = self.ui.findChild(QtWidgets.QPushButton, 'verticalLayout')
        self.ui.pushButton_Save = self.ui.findChild(QtWidgets.QPushButton, 'pushButton_Save')
        self.ui.scrollAreaWidgetContents = self.ui.findChild(QtWidgets.QWidget, 'scrollAreaWidgetContents')
        self.ui.pushButton_Save.clicked.connect(self.save_asset)
        self.ui.pushButton_Save.setStyleSheet(get_add_row_style())
        self.inputs = {}
        inner_widget = self.ui.scrollAreaWidgetContents  # This is the auto-generated QWidget
        # Set a layout if not already set
        if not self.ui.scrollAreaWidgetContents.layout():
            layout = QtWidgets.QVBoxLayout(self.ui.scrollAreaWidgetContents)
            layout.setMargin(0)
        else:
            layout = self.ui.scrollAreaWidgetContents.layout()

        ## Here we need to get all the selecteds
        selected = get_selected_assets()
        i = 0
        for asset in selected:
            print(f"MetadataEditor: Editing Asset: {asset}")
            existing_tags = get_asset_metadata(asset)
            if existing_tags:
                layout.addWidget(self.add_entry(asset, "Empty", i))
                layout.adjustSize()
            i+=1
            
        ## Line for a new value
        ## self.add_entry("", "", i+1)
        button = QtWidgets.QPushButton(f"+")
        button.clicked.connect(self.add_new_row)
        button.setStyleSheet(get_add_row_style())
        layout.addWidget(button)

        
    def add_entry(self, key = "None", value = "Empty", index = 0):
        new_entry_row = QtWidgets.QHBoxLayout(self)
        new_label = QtWidgets.QLabel(f"Label_{index}")
        value_input = QtWidgets.QLineEdit(f"Label_{index}") 
        new_label.setText(f"{key}")
        new_label.setStyleSheet(get_add_row_style())
        value_input.setStyleSheet(get_add_row_style())
        new_entry_row.addWidget(new_label)
        new_entry_row.addWidget(value_input)
        return new_entry_row
        
    def add_empty_entry(self):
        new_key = f"Key {len(self.inputs) + 1}"
        self.add_entry(new_key, "")
        self.layout.adjustSize()
        self.scroll_area.ensureWidgetVisible(self.inputs[new_key])
    
    def get_data(self):
        return {key: input_field.text() for key, input_field in self.inputs.items()}
    
    def save_asset(self):
        print(f"Saved!")
        return
    
    def add_new_row(self):
        self.add_entry("None", "Empty", 0)
        self.adjustSize()
        return