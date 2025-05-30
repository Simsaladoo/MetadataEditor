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


class MetadataRow(QtWidgets.QWidget):
    log_debug = QtCore.Signal(str)
    status_changed = QtCore.Signal(bool)
    def __init__(self, asset):
        super(MetadataRow, self).__init__()
        self.asset = asset
        layout = QtWidgets.QHBoxLayout(self)
        layout.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)

        self.label = QtWidgets.QLabel(str(asset).split(".")[-1])
        self.label.setStyleSheet("color: #ffffff;")
        self.label.setMargin(4)
        layout.addWidget(self.label)

        self.key = QtWidgets.QTextEdit("")
        self.key.setStyleSheet("color: #ffffff;")
        self.key.textChanged.connect(self.handle_key_changed)
        layout.addWidget(self.key)

        self.value = QtWidgets.QTextEdit("")
        self.value.setStyleSheet("color: #ffffff;")
        self.value.textChanged.connect(self.handle_value_changed)
        layout.addWidget(self.value)

        self.button_add = QtWidgets.QPushButton("+")
        self.button_subtract = QtWidgets.QPushButton("-")
        self.button_add.setFixedWidth(50)
        self.button_add.setMinimumHeight(20)
        self.button_add.setStyleSheet("color: #98FB98;")
        self.button_subtract.setFixedWidth(50)
        self.button_subtract.setMinimumHeight(20)
        self.button_subtract.setStyleSheet("color: #FFB3B3;")
        layout.addWidget(self.button_subtract)
        layout.addWidget(self.button_add)

        existing_tags = metadata_editor.get_asset_metadata(asset)
        print(f"{asset}: {existing_tags}")
        self.setLayout(layout)

    def get_key(self):
        return self.key.toPlainText()

    def get_value(self):
        return self.value.toPlainText()

    def handle_key_changed(self):
        current_text = self.get_key()
        return current_text

    def handle_value_changed(self):
        current_text = self.get_value()
        return current_text


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
        self.setStyleSheet("background-color: #1d1d1d;")
        self.setObjectName('MetadataEditorWidget')
        self.setWindowTitle('Metadata Editor')
        self.resize(500,50)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)
        layout.addWidget(self.ui)
        self.rows = []
        self.setLayout(layout)
        verticalLayout = self.ui.findChild(QtWidgets.QVBoxLayout, 'verticalLayout')
        self.init_ui(verticalLayout)
        self.button_save = QtWidgets.QPushButton("Save")
        self.button_save.setStyleSheet("background-color: #D3D3D3;")
        self.button_save.setDisabled(True)
        layout.addWidget(self.button_save)


    def init_ui(self, verticalLayout):
        selected = metadata_editor.get_selected_assets()
        if not len(selected) > 0:
            return
        path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))) + "/Resources/Icon128.png"
        self.ui.setWindowIcon(QtGui.QIcon(path))
        self.inputs = {}
        selected = metadata_editor.get_selected_assets()
        for asset in selected:
            row = MetadataRow(asset)
            row.status_changed.connect(self.on_status_changed)
            self.rows.append(row)
            verticalLayout.addWidget(row)
        new_length = len(selected) * 25 + 25
        self.resize(500,new_length)




    def get_data(self):
        return {key: input_field.text() for key, input_field in self.inputs.items()}

    def save_asset(self):
        print(f"Saved!")
        return



    def on_status_changed(self, status):
        print(f"Metadata Editor: {status}")
        self.button_save.setEnabled(True)
        self.button_save.setStyleSheet("background-color: #98FB98;")


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