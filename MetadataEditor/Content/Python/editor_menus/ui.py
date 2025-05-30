from PySide2 import QtUiTools, QtWidgets, QtCore, QtGui
from editor_menus import metadata_editor
import os
import sys
import unreal

'''
from editor_menus import ui, metadata_editor
from importlib import reload
reload(ui)
reload(metadata_editor)
metadata_editor.open_window()
'''


def get_add_row_style():
    green_button_hover_style = """
        QPushButton {background-color: rgb(30,55,44);color: white;}
        QPushButton::hover {background-color: rgb(60,110,88);color: white;}
        QLabel {color: rgb(30,55,44);color: white;}  
        """
    return green_button_hover_style


class MetadataEditorWidget(QtWidgets.QWidget):
    def __init__(self):
        super(MetadataEditorWidget, self).__init__()
        self.paths = []
        widgetPath = f'{os.path.dirname(os.path.abspath(__file__))}/form.ui'
        self.ui = QtUiTools.QUiLoader().load(widgetPath)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setMargin(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.setObjectName('MetadataEditorWidget')
        self.setWindowTitle('Metadata Editor')
        self.resize(400,250)
        self.label = QtWidgets.QLabel("Metadata Editor")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)
        layout.addWidget(self)
        self.init_ui()


    def init_ui(self):
        selected = metadata_editor.get_selected_assets()
        if not len(selected) > 0:
            return
        path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))) + "/Resources/Icon128.png"
        self.ui.setWindowIcon(QtGui.QIcon(path))
        self.inputs = {}
        selected = metadata_editor.get_selected_assets()
        for asset in selected:
            print(f"MetadataEditor: Editing Asset: {asset}")
            existing_tags = metadata_editor.get_asset_metadata(asset)
            print(f"{asset}: {existing_tags}")




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

app = None
def open_window():
    global app
    if QtWidgets.QApplication.instance():
        for win in (QtWidgets.QApplication.allWindows()):
            if 'Metadata' in win.objectName():
                print(f'Destroying previous window: {win}')
                win.destroy()
    else:
        QtWidgets.QApplication(sys.argv)
    app = MetadataEditorWidget()
    app.show()
    app.activateWindow()
    unreal.parent_external_window_to_slate(app.winId(), unreal.SlateParentWindowSearchMethod.MAIN_WINDOW)
    return app