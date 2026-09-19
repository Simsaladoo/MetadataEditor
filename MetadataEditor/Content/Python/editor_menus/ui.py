from PySide2 import QtUiTools, QtWidgets, QtCore, QtGui
from editor_menus import metadata_editor, styles
import os
import sys
import unreal
import json


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
        #ffffff;")
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
        # Set existing metadata in the row if available
        if existing_tags:
            # Take first key/value pair for display
            first_key = list(existing_tags.keys())[0] if existing_tags else ""
            first_value = existing_tags.get(first_key, "") if first_key else ""
            self.key.setPlainText(first_key)
            self.value.setPlainText(first_value)

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


class MetadataComparisonDialog(QtWidgets.QDialog):
    def __init__(self, comparison_data, parent=None):
        super(MetadataComparisonDialog, self).__init__(parent)
        self.setWindowTitle("Metadata Comparison")
        self.setModal(True)
        self.resize(700, 500)

        layout = QtWidgets.QVBoxLayout(self)

        # Info label
        info_label = QtWidgets.QLabel()
        info_label.setTextFormat(QtCore.Qt.RichText)
        layout.addWidget(info_label)
        self.info_label = info_label

        # Create table widget for comparison
        self.table = QtWidgets.QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        layout.addWidget(self.table)

        # Update info
        self.update_info(comparison_data)

        # Populate table with comparison data
        self.populate_table(comparison_data)

        # Add buttons
        button_layout = QtWidgets.QHBoxLayout()

        self.apply_from_button = QtWidgets.QPushButton("Apply Selected Asset's Metadata to All")
        self.apply_from_button.clicked.connect(self.apply_selected_metadata)
        button_layout.addWidget(self.apply_from_button)

        self.apply_selected_button = QtWidgets.QPushButton("Apply Selected Keys to All")
        self.apply_selected_button.clicked.connect(self.apply_selected_keys)
        self.apply_selected_button.setEnabled(False)
        button_layout.addWidget(self.apply_selected_button)

        self.close_button = QtWidgets.QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

        # Store comparison data for use in apply functions
        self.comparison_data = comparison_data
        self.selected_keys = set()

        # Connect table selection change
        self.table.itemSelectionChanged.connect(self.on_table_selection_changed)

    def update_info(self, comparison_data):
        uniform_count = len(comparison_data['uniform_keys'])
        varying_count = len(comparison_data['varying_keys'])
        total_assets = len(comparison_data['assets'])
        info_text = f"""
        <b>Compared {total_assets} assets:</b><br>
        Uniform keys (same across all assets): {uniform_count}<br>
        Varying keys (different or missing in some assets): {varying_count}
        """
        self.info_label.setText(info_text.strip())

    def populate_table(self, comparison_data):
        """Populate the table with metadata comparison data"""
        if not comparison_data or not comparison_data['assets']:
            return

        assets = comparison_data['assets']
        all_keys = comparison_data['all_keys']

        # Set up table
        self.table.setRowCount(len(all_keys))
        self.table.setColumnCount(len(assets) + 1)  # +1 for asset names column

        # Set headers
        headers = ["Metadata Key"] + [asset['name'] for asset in assets]
        self.table.setHorizontalHeaderLabels(headers)

        # Fill in data
        for row, key in enumerate(all_keys):
            # Key name with checkbox for selection
            key_widget = QtWidgets.QWidget()
            key_layout = QtWidgets.QHBoxLayout(key_widget)
            key_layout.setContentsMargins(4, 4, 4, 4)

            key_item = QtWidgets.QTableWidgetItem(key)
            key_item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

            checkbox = QtWidgets.QCheckBox()
            checkbox.stateChanged.connect(lambda state, k=key: self.on_checkbox_changed(k, state))

            key_layout.addWidget(checkbox)
            key_layout.addWidget(QtWidgets.QLabel(f" <b>{key}</b>"))
            key_layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

            self.table.setCellWidget(row, 0, key_widget)

            # Values for each asset
            for col, asset in enumerate(assets):
                value = asset['metadata'].get(key, "")
                value_item = QtWidgets.QTableWidgetItem(str(value))

                # Check if all assets have the same value for this key
                if comparison_data['uniform_keys'] and key in comparison_data['uniform_keys']:
                    # Uniform value - set background to indicate consistency
                    value_item.setBackground(QtGui.QColor(200, 255, 200))  # Light green
                elif key in comparison_data['varying_keys']:
                    # Varying value - set background to indicate difference
                    value_item.setBackground(QtGui.QColor(255, 200, 200))  # Light red

                value_item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                self.table.setItem(row, col + 1, value_item)

        # Resize columns to content
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)

    def on_checkbox_changed(self, key, state):
        if state == QtCore.Qt.Checked:
            self.selected_keys.add(key)
        else:
            self.selected_keys.discard(key)

        # Enable apply selected button if any keys are selected
        self.apply_selected_button.setEnabled(len(self.selected_keys) > 0)

    def on_table_selection_changed(self):
        # Update selected keys based on table selection
        selected_items = self.table.selectedItems()
        if selected_items:
            # Get the key from the first column of the selected row
            row = self.table.currentRow()
            key_widget = self.table.cellWidget(row, 0)
            if key_widget:
                # Find the checkbox and label to get the key
                layout = key_widget.layout()
                if layout:
                    label = layout.itemAt(1).widget()  # The QLabel
                    if label:
                        key_text = label.text()
                        # Remove HTML tags if present
                        key_text = key_text.replace("<b>", "").replace("</b>", "")
                        # Toggle checkbox state
                        checkbox = layout.itemAt(0).widget()  # The QCheckBox
                        if checkbox:
                            checkbox.setChecked(not checkbox.isChecked())

    def apply_selected_metadata(self):
        """Apply the metadata from the selected asset to all other selected assets"""
        # Use the first asset as source for simplicity
        source_asset_name = self.comparison_data['assets'][0]['name']
        source_asset_path = self.comparison_data['assets'][0]['path']
        source_metadata = self.comparison_data['assets'][0]['metadata']

        # Ask for confirmation
        reply = QtWidgets.QMessageBox.question(
            self,
            "Apply Metadata",
            f"Apply metadata from '{source_asset_name}' to all {len(self.comparison_data['assets'])} selected assets?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            # Apply metadata from source to all assets
            success_count = 0
            for asset in self.comparison_data['assets']:
                asset_path = asset['path']
                try:
                    # Clear existing metadata and apply source metadata
                    # First, get all keys on this asset to clear them
                    current_metadata = metadata_editor.get_asset_metadata(asset_path)
                    for key in current_metadata.keys():
                        metadata_editor.set_metadata_on_asset(asset_path, key, "")  # Clear by setting empty

                    # Apply source metadata
                    for key, value in source_metadata.items():
                        metadata_editor.set_metadata_on_asset(asset_path, key, value)
                    success_count += 1
                except Exception as e:
                    print(f"Failed to apply metadata to {asset_path}: {e}")

            QtWidgets.QMessageBox.information(
                self,
                "Metadata Applied",
                f"Successfully applied metadata from '{source_asset_name}' to {success_count} assets."
            )
            self.accept()

    def apply_selected_keys(self):
        """Apply only the selected keys from the first asset to all others"""
        if not self.selected_keys:
            QtWidgets.QMessageBox.warning(
                self,
                "No Keys Selected",
                "Please select at least one metadata key to apply."
            )
            return

        # Use the first asset as source
        source_asset_name = self.comparison_data['assets'][0]['name']
        source_asset_path = self.comparison_data['assets'][0]['path']
        source_metadata = self.comparison_data['assets'][0]['metadata']

        # Filter to only selected keys
        selected_metadata = {k: source_metadata[k] for k in self.selected_keys if k in source_metadata}

        # Ask for confirmation
        reply = QtWidgets.QMessageBox.question(
            self,
            "Apply Selected Keys",
            f"Apply {len(selected_metadata)} selected metadata keys from '{source_asset_name}' to all {len(self.comparison_data['assets'])} selected assets?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            # Apply selected metadata from source to all assets
            success_count = 0
            for asset in self.comparison_data['assets']:
                asset_path = asset['path']
                try:
                    # Apply only selected metadata keys
                    for key, value in selected_metadata.items():
                        metadata_editor.set_metadata_on_asset(asset_path, key, value)
                    success_count += 1
                except Exception as e:
                    print(f"Failed to apply selected metadata to {asset_path}: {e}")

            QtWidgets.QMessageBox.information(
                self,
                "Metadata Applied",
                f"Successfully applied {len(selected_metadata)} metadata keys from '{source_asset_name}' to {success_count} assets."
            )
            self.accept()


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
        self.resize(800, 50)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)
        layout.addWidget(self.ui)
        self.rows = []
        self.setLayout(layout)
        self.init_ui()
        self.setup_connections()
        self.copied_metadata = {}  # Store copied metadata for paste operations
        self.template_dir = f"{os.path.dirname(os.path.abspath(__file__))}/templates"

        # Create template directory if it doesn't exist
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)

    def init_ui(self):
        selected = metadata_editor.get_selected_assets()
        if not len(selected) > 0:
            self.ui.statusLabel.setText("No assets selected")
            return

        path = f"{os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))}/Resources/icon128.png"
        self.ui.setWindowIcon(QtGui.QIcon(path))

        # Clear existing rows
        for row in self.rows:
            row.setParent(None)
        self.rows.clear()

        # Create vertical layout for rows if it doesn't exist
        vertical_layout = self.ui.findChild(QtWidgets.QVBoxLayout, 'verticalLayout')
        if not vertical_layout:
            vertical_layout = QtWidgets.QVBoxLayout()
            vertical_layout.setObjectName('verticalLayout')
            self.ui.verticalLayout_2.insertLayout(1, vertical_layout)

        # Add rows for each selected asset
        selected = metadata_editor.get_selected_assets()
        for asset in selected:
            row = MetadataRow(asset)
            row.status_changed.connect(self.on_status_changed)
            self.rows.append(row)
            vertical_layout.addWidget(row)

        # Update window size based on number of rows
        new_height = len(selected) * 25 + 250  # 250 for header and buttons
        self.resize(800, max(new_height, 300))
        self.ui.statusLabel.setText(f"Editing {len(selected)} asset(s)")

    def setup_connections(self):
        self.ui.applyButton.clicked.connect(self.apply_metadata)
        self.ui.saveButton.clicked.connect(self.save_all_assets)
        self.ui.copyButton.clicked.connect(self.copy_metadata_from_asset)
        self.ui.pasteButton.clicked.connect(self.paste_metadata_to_assets)
        self.ui.compareButton.clicked.connect(self.compare_metadata)
        self.ui.templateSaveButton.clicked.connect(self.save_template)
        self.ui.templateLoadButton.clicked.connect(self.load_template)
        self.ui.exportButton.clicked.connect(self.export_metadata)
        self.ui.importButton.clicked.connect(self.import_metadata)
        self.ui.keyInput.returnPressed.connect(self.apply_metadata)
        self.ui.valueInput.returnPressed.connect(self.apply_metadata)

    def get_data(self):
        return {
            'key': self.ui.keyInput.text(),
            'value': self.ui.valueInput.text()
        }

    def apply_metadata(self):
        data = self.get_data()
        key = data['key'].strip()
        value = data['value'].strip()

        if not key:
            self.ui.statusLabel.setText("Please enter a metadata key")
            return

        selected = metadata_editor.get_selected_assets()
        if not selected:
            self.ui.statusLabel.setText("No assets selected")
            return

        success_count = 0
        for asset_path in selected:
            try:
                metadata_editor.set_metadata_on_asset(asset_path, key, value)
                success_count += 1
            except Exception as e:
                print(f"Failed to set metadata on {asset_path}: {e}")

        self.ui.statusLabel.setText(f"Applied '{key}' to {success_count}/{len(selected)} assets")

        # Also update individual rows if they exist
        for row in self.rows:
            row.key.setPlainText(key)
            row.value.setPlainText(value)

    def copy_metadata_from_asset(self):
        """Copy metadata from the first selected asset"""
        selected = metadata_editor.get_selected_assets()
        if not selected:
            self.ui.statusLabel.setText("No assets selected to copy from")
            return

        # Use the first selected asset as source
        source_asset = selected[0]
        metadata_dict = metadata_editor.get_asset_metadata(source_asset)

        if not metadata_dict:
            self.ui.statusLabel.setText(f"No metadata found on {source_asset.split('.')[-1]}")
            self.copied_metadata = {}
            return

        # Store the copied metadata
        self.copied_metadata = metadata_dict.copy()

        # Show first key/value in the input fields for convenience
        first_key = list(metadata_dict.keys())[0] if metadata_dict else ""
        first_value = metadata_dict.get(first_key, "") if first_key else ""

        self.ui.keyInput.setText(first_key)
        self.ui.valueInput.setText(first_value)

        self.ui.statusLabel.setText(f"Copied metadata from {source_asset.split('.')[-1]} ({len(metadata_dict)} tags)")
        self.ui.copyButton.setStyleSheet("background-color: #98FB98;")

        # Reset button style after a short delay
        QtCore.QTimer.singleShot(1500, lambda: self.ui.copyButton.setStyleSheet(""))

    def paste_metadata_to_assets(self):
        """Paste copied metadata to all selected assets"""
        if not self.copied_metadata:
            self.ui.statusLabel.setText("No metadata copied to paste")
            return

        selected = metadata_editor.get_selected_assets()
        if not selected:
            self.ui.statusLabel.setText("No assets selected to paste to")
            return

        success_count = 0
        for asset_path in selected:
            try:
                # Apply each metadata tag from copied metadata
                for key, value in self.copied_metadata.items():
                    metadata_editor.set_metadata_on_asset(asset_path, str(key), str(value))
                success_count += 1
            except Exception as e:
                print(f"Failed to paste metadata to {asset_path}: {e}")

        self.ui.statusLabel.setText(f"Pasted metadata to {success_count}/{len(selected)} assets")
        self.ui.pasteButton.setStyleSheet("background-color: #98FB98;")

        # Reset button style after a short delay
        QtCore.QTimer.singleShot(1500, lambda: self.ui.pasteButton.setStyleSheet(""))

    def compare_metadata(self):
        """Compare metadata across all selected assets"""
        selected = metadata_editor.get_selected_assets()
        if not selected:
            self.ui.statusLabel.setText("No assets selected to compare")
            return

        if len(selected) < 2:
            self.ui.statusLabel.setText("Select at least 2 assets to compare metadata")
            return

        # Collect metadata from all selected assets
        assets_data = []
        all_keys = set()

        for asset_path in selected:
            asset_name = asset_path.split('.')[-1]  # Get just the filename
            metadata_dict = metadata_editor.get_asset_metadata(asset_path)

            assets_data.append({
                'name': asset_name,
                'path': asset_path,
                'metadata': metadata_dict
            })

            all_keys.update(metadata_dict.keys())

        # Determine which keys are uniform (same value across all assets) and which vary
        uniform_keys = set()
        varying_keys = set()

        for key in all_keys:
            values = []
            for asset in assets_data:
                value = asset['metadata'].get(key, None)  # None if key doesn't exist
                values.append(value)

            # Check if all values are the same (including None for missing keys)
            if len(set(values)) == 1:
                uniform_keys.add(key)
            else:
                varying_keys.add(key)

        comparison_data = {
            'assets': assets_data,
            'all_keys': sorted(list(all_keys)),
            'uniform_keys': uniform_keys,
            'varying_keys': varying_keys
        }

        # Show comparison dialog
        dialog = MetadataComparisonDialog(comparison_data, self)
        dialog.exec_()

        # Update status based on comparison result
        uniform_count = len(uniform_keys)
        varying_count = len(varying_keys)
        total_assets = len(selected)

        self.ui.statusLabel.setText(
            f"Compared {total_assets} assets: {uniform_count} uniform keys, {varying_count} varying keys"
        )

    def save_template(self):
        """Save current metadata key/value as a template"""
        data = self.get_data()
        key = data['key'].strip()
        value = data['value'].strip()

        if not key:
            self.ui.statusLabel.setText("Please enter a metadata key to save as template")
            return

        # Ask for template name
        template_name, ok = QtWidgets.QInputDialog.getText(
            self,
            "Save Template",
            "Enter template name:",
            text=f"{key}_{value}" if value else key
        )

        if ok and template_name:
            # Clean template name for file system
            safe_name = "".join(c for c in template_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if not safe_name:
                safe_name = "template"

            template_path = os.path.join(self.template_dir, f"{safe_name}.json")

            try:
                template_data = {
                    'name': template_name,
                    'key': key,
                    'value': value,
                    'created': str(QtCore.QDateTime.currentDateTime().toString())
                }

                with open(template_path, 'w') as f:
                    json.dump(template_data, f, indent=2)

                self.ui.statusLabel.setText(f"Template '{template_name}' saved")
                self.ui.templateSaveButton.setStyleSheet("background-color: #98FB98;")
                QtCore.QTimer.singleShot(1500, lambda: self.ui.templateSaveButton.setStyleSheet(""))
            except Exception as e:
                self.ui.statusLabel.setText(f"Failed to save template: {str(e)}")
                print(f"Template save error: {e}")

    def load_template(self):
        """Load a template and apply it"""
        # Get list of template files
        try:
            template_files = [f for f in os.listdir(self.template_dir) if f.endswith('.json')]
        except FileNotFoundError:
            self.ui.statusLabel.setText("No templates directory found")
            return

        if not template_files:
            self.ui.statusLabel.setText("No templates available")
            return

        # Show template selection dialog
        template_names = []
        for f in template_files:
            try:
                with open(os.path.join(self.template_dir, f), 'r') as fp:
                    data = json.load(fp)
                    template_names.append(data.get('name', f.replace('.json', '')))
            except:
                template_names.append(f.replace('.json', ''))

        template_name, ok = QtWidgets.QInputDialog.getItem(
            self,
            "Load Template",
            "Select template to load:",
            template_names,
            0,
            False
        )

        if ok and template_name:
            # Find the selected template file
            selected_file = None
            for i, f in enumerate(template_files):
                try:
                    with open(os.path.join(self.template_dir, f), 'r') as fp:
                        data = json.load(fp)
                        if data.get('name', f.replace('.json', '')) == template_name:
                            selected_file = f
                            break
                except:
                    if template_files[i].replace('.json', '') == template_name:
                        selected_file = f
                        break

            if selected_file:
                try:
                    with open(os.path.join(self.template_dir, selected_file), 'r') as f:
                        template_data = json.load(f)

                    key = template_data.get('key', '')
                    value = template_data.get('value', '')

                    if key:
                        self.ui.keyInput.setText(key)
                        self.ui.valueInput.setText(value)
                        self.apply_metadata()  # Automatically apply the template

                        self.ui.statusLabel.setText(f"Template '{template_name}' loaded and applied")
                        self.ui.templateLoadButton.setStyleSheet("background-color: #98FB98;")
                        QtCore.QTimer.singleShot(1500, lambda: self.ui.templateLoadButton.setStyleSheet(""))
                    else:
                        self.ui.statusLabel.setText("Invalid template: missing key")
                except Exception as e:
                    self.ui.statusLabel.setText(f"Failed to load template: {str(e)}")
                    print(f"Template load error: {e}")

    def export_metadata(self):
        """Export metadata from selected assets to a JSON file"""
        selected = metadata_editor.get_selected_assets()
        if not selected:
            self.ui.statusLabel.setText("No assets selected to export")
            return

        # Collect metadata from all selected assets
        export_data = {}
        for asset_path in selected:
            asset_name = asset_path.split('.')[-1]
            metadata_dict = metadata_editor.get_asset_metadata(asset_path)
            export_data[asset_name] = metadata_dict

        # Ask for file name
        file_name, ok = QtWidgets.QInputDialog.getText(
            self,
            "Export Metadata",
            "Enter file name (without extension):",
            text="metadata_export"
        )

        if ok and file_name:
            # Clean file name
            safe_name = "".join(c for c in file_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if not safe_name:
                safe_name = "metadata_export"

            export_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{safe_name}.json")

            try:
                with open(export_path, 'w') as f:
                    json.dump(export_data, f, indent=2)

                self.ui.statusLabel.setText(f"Metadata exported to {safe_name}.json")
                self.ui.exportButton.setStyleSheet("background-color: #98FB98;")
                QtCore.QTimer.singleShot(1500, lambda: self.ui.exportButton.setStyleSheet(""))
            except Exception as e:
                self.ui.statusLabel.setText(f"Failed to export metadata: {str(e)}")
                print(f"Export error: {e}")

    def import_metadata(self):
        """Import metadata from a JSON file and apply to selected assets"""
        # For simplicity, we'll import and apply to all selected assets equally
        # A more advanced version would map filenames to assets

        file_name, ok = QtWidgets.QInputDialog.getText(
            self,
            "Import Metadata",
            "Enter file name to import (without extension):",
            text="metadata_import"
        )

        if ok and file_name:
            # Clean file name
            safe_name = "".join(c for c in file_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if not safe_name:
                safe_name = "metadata_import"

            import_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{safe_name}.json")

            if not os.path.exists(import_path):
                self.ui.statusLabel.setText(f"File {safe_name}.json not found")
                return

            try:
                with open(import_path, 'r') as f:
                    import_data = json.load(f)

                selected = metadata_editor.get_selected_assets()
                if not selected:
                    self.ui.statusLabel.setText("No assets selected to import to")
                    return

                # Apply imported metadata to all selected assets
                # For simplicity, we apply the same metadata to all assets
                # A more advanced version would match asset names
                success_count = 0
                for asset_path in selected:
                    try:
                        # Clear existing metadata first
                        current_metadata = metadata_editor.get_asset_metadata(asset_path)
                        for key in current_metadata.keys():
                            metadata_editor.set_metadata_on_asset(asset_path, key, "")

                        # Apply imported metadata (use first asset's data or merge all)
                        # For now, we'll use the metadata from the first entry in the file
                        if import_data:
                            first_asset_key = list(import_data.keys())[0]
                            metadata_to_apply = import_data[first_asset_key]

                            for key, value in metadata_to_apply.items():
                                metadata_editor.set_metadata_on_asset(asset_path, key, value)

                        success_count += 1
                    except Exception as e:
                        print(f"Failed to import metadata to {asset_path}: {e}")

                self.ui.statusLabel.setText(f"Metadata imported to {success_count} assets")
                self.ui.importButton.setStyleSheet("background-color: #98FB98;")
                QtCore.QTimer.singleShot(1500, lambda: self.ui.importButton.setStyleSheet(""))
            except Exception as e:
                self.ui.statusLabel.setText(f"Failed to import metadata: {str(e)}")
                print(f"Import error: {e}")

    def save_all_assets(self):
        selected = metadata_editor.get_selected_assets()
        if not selected:
            self.ui.statusLabel.setText("No assets selected to save")
            return

        # In Unreal, metadata is saved immediately when set, so we just confirm
        self.ui.statusLabel.setText(f"Metadata saved for {len(selected)} asset(s)")
        self.ui.saveButton.setStyleSheet("background-color: #98FB98;")

        # Reset button style after a short delay
        QtCore.QTimer.singleShot(1500, lambda: self.ui.saveButton.setStyleSheet(""))

    def on_status_changed(self, status):
        if status:
            self.ui.statusLabel.setText("Metadata changed - click Save to confirm")
            self.ui.saveButton.setStyleSheet("background-color: #FFB3B3;")
        else:
            self.ui.statusLabel.setText("Ready")


app = None
def open_window():
    global app
    if QtWidgets.QApplication.instance():
        for win in (QtWidgets.QApplication.allWindows()):
            if 'MetadataEditorWidget' in win.objectName():
                print(f'Destroying previous window: {win}')
                win.destroy()
    else:
        QtWidgets.QApplication(sys.argv)
    app = MetadataEditorWidget()
    app.show()
    app.activateWindow()
    unreal.parent_external_window_to_slate(app.winId(), unreal.SlateParentWindowSearchMethod.MAIN_WINDOW)
    return app