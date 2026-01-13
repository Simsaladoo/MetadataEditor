from PySide2 import QtUiTools, QtWidgets, QtCore, QtGui
from editor_menus import metadata_editor, styles
import os
import sys
import unreal

'''
from editor_menus import ui, metadata_editor, styles
from importlib import reload
reload(ui)
reload(styles)
reload(metadata_editor)
ui.open_window()
'''




class MetadataEditorWidget(QtWidgets.QWidget):
    def __init__(self):
        super(MetadataEditorWidget, self).__init__()
        self.paths = []
        widgetPath = f'{os.path.dirname(os.path.abspath(__file__))}/form.ui'
        self.ui = QtUiTools.QUiLoader().load(widgetPath)
        window = QtWidgets.QVBoxLayout(self)
        layout = QtWidgets.QHBoxLayout(self)
        controls = QtWidgets.QHBoxLayout(self)
        grid = QtWidgets.QVBoxLayout(self)
        text = QtWidgets.QVBoxLayout(self)
        path = f"{os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))}/Resources/icon.ico"
        print(f"Icon path: {path}")
        self.ui.setWindowIcon(QtGui.QIcon(path))
        layout.setMargin(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        controls.setMargin(0)
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(2)
        self.setStyleSheet(styles.widget_background)
        self.setObjectName('MetadataEditorWidget')
        self.setWindowTitle('Metadata Bulk Editor')
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)
        window.addWidget(self.ui)
        layout.addLayout(grid) 
        selected = metadata_editor.get_selected_assets()
        for asset in selected:
            self.label = QtWidgets.QLabel(str(asset).split(".")[-1])
            self.label.setStyleSheet(styles.grid_background)
            self.label.setMargin(6)
            self.label.setMinimumWidth(250)
            grid.addWidget(self.label)
        self.resize(500, len(selected) * 25 + 25)
        window.addLayout(controls)
        self.rows = []
        self.setLayout(window)
        
        
        
        
        
        # These need to be able to be spawned multiple times
        # Keys
        self.key_label = QtWidgets.QLabel(" Key: ")
        self.key_label.setStyleSheet(styles.white_text_style)
        controls.addWidget(self.key_label)
        self.key = QtWidgets.QTextEdit("")
        self.key.setStyleSheet(styles.white_text_style)
        self.key.setMaximumHeight(35)
        controls.addWidget(self.key)

        # Values
        self.value_label = QtWidgets.QLabel(" Value: ")
        self.value_label.setStyleSheet(styles.white_text_style)
        controls.addWidget(self.value_label)
        self.value = QtWidgets.QTextEdit("")
        self.value.setStyleSheet(styles.white_text_style)
        self.value.setMaximumHeight(35)
        controls.addWidget(self.value)
        
        
        # Add Row Button
        self.button_add = QtWidgets.QPushButton("+")
        self.button_add.setFixedWidth(50)
        self.button_add.setMinimumHeight(35)
        self.button_add.setStyleSheet(styles.green_button_hover_style)
        controls.addWidget(self.button_add)
        
        # Clear Row Button
        self.button_subtract = QtWidgets.QPushButton("-")
        self.button_subtract.setFixedWidth(50)
        self.button_subtract.setMinimumHeight(35)
        self.button_subtract.setStyleSheet(styles.red_button_hover_style)
        controls.addWidget(self.button_subtract)
            
        # Save button
        self.button_save = QtWidgets.QPushButton("Save")
        self.button_save.setMinimumHeight(35)
        self.button_save.setStyleSheet(styles.green_button_hover_style)
        window.addWidget(self.button_save)
        


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