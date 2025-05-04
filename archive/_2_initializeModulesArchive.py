import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QCheckBox, QListWidget
from PyQt5.QtCore import Qt, QEvent, QTimer
from PyQt5.QtGui import QStandardItem, QFontMetrics, QPalette
import states.statesAllRequests as statesAllRequests
import states.statesAllRequests as statesAllRequests
import database.tableSetup as tableSetup
import hooks.csiHooks as csiHooks

class ModulesScreen(QMainWindow):
    def __init__(self):
        super(ModulesScreen, self).__init__()
        loadUi("qtDesigner/windowModules.ui",self)
        self.initiliazeUI()

    def initiliazeUI(self):
        # Set the number of columns based on the total spans + 1 for checkbox column
        total_columns = sum(tableSetup.mainHeaderspans) + 1
        self.mainTableWidget.setColumnCount(total_columns)
        # Set the number of rows based on Requests length + 2 (1 for main headers, 1 for subheaders)
        self.mainTableWidget.setRowCount(len(statesAllRequests.Requests) + 2)
        # Hide the vertical header
        self.mainTableWidget.verticalHeader().setVisible(False)
        # Set table widget to expand and fill its container
        self.mainTableWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.mainTableWidget.horizontalHeader().setStretchLastSection(True)
        self.mainTableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # Set fixed width for checkbox column
        self.mainTableWidget.setColumnWidth(0, 30)  # 30 pixels wide for checkbox column
        
        # Add main headers with spans (starting from column 1)
        current_col = 1  # Start from column 1 to leave space for checkbox column
        for header, span in zip(tableSetup.mainHeaders, tableSetup.mainHeaderspans):
            item = QTableWidgetItem(header)
            self.mainTableWidget.setItem(0, current_col, item)
            self.mainTableWidget.setSpan(0, current_col, 1, span)
            current_col += span
            
        # Add subheaders (starting from column 1)
        current_col = 1
        subheader_index = 0
        for span in tableSetup.mainHeaderspans:
            for _ in range(span):
                if subheader_index < len(tableSetup.subHeaders):
                    item = QTableWidgetItem(tableSetup.subHeaders[subheader_index])
                    self.mainTableWidget.setItem(1, current_col, item)
                    current_col += 1
                    subheader_index += 1
                    
        # Map Requests data to rows
        for row_idx, request in enumerate(statesAllRequests.Requests, start=2):  # Start from row 2 (after headers)
            current_col = 0  # Start from column 0 for checkbox
            
            # Add checkbox for Selected
            checkbox = QCheckBox()
            checkbox.setChecked(request.get("Selected", False))
            checkbox.setStyleSheet("margin-left: 6px;")
            self.mainTableWidget.setCellWidget(row_idx, current_col, checkbox)
            current_col += 1
            
            # Map remaining values based on cellWidgets
            for key, widget_type in tableSetup.cellWidgets.items():
                if key == "Selected":
                    continue  # Skip Selected as we already handled it
                    
                value = request.get(key, "")
                
                if widget_type == "checkbox":
                    checkbox = QCheckBox()
                    checkbox.setChecked(bool(value))
                    checkbox.setStyleSheet("margin-left: 6px;")
                    self.mainTableWidget.setCellWidget(row_idx, current_col, checkbox)
                elif widget_type == "combobox":
                    combo = QtWidgets.QComboBox()
                    if key == "Run":
                        combo.addItems(tableSetup.runOptions)
                    elif key == "DataType":
                        combo.addItems(list(tableSetup.dataOptions.keys()))
                        # Connect signal for Data combobox update
                        def update_data_combo(data_type, row, col):
                            data_combo = self.mainTableWidget.cellWidget(row, col + 1)  # Data combobox is next column
                            if data_combo:
                                data_combo.clear()
                                if data_type in tableSetup.dataOptions:
                                    data_combo.addItems(tableSetup.dataOptions[data_type])
                        combo.currentTextChanged.connect(lambda text, r=row_idx, c=current_col: update_data_combo(text, r, c))
                        # Set initial value and trigger update
                        if value:
                            combo.setCurrentText(value)
                            update_data_combo(value, row_idx, current_col)
                    elif key == "Data":
                        # Data combobox will be populated based on DataType selection
                        combo.addItems([])  # Initially empty, will be populated when DataType changes
                        # Get the current DataType value and populate accordingly
                        data_type_combo = self.mainTableWidget.cellWidget(row_idx, current_col - 1)  # DataType is previous column
                        if data_type_combo:
                            current_data_type = data_type_combo.currentText()
                            if current_data_type in tableSetup.dataOptions:
                                combo.addItems(tableSetup.dataOptions[current_data_type])
                    elif key == "LoadCase":
                        combo.addItems(tableSetup.LoadCombinationNames)
                    elif key == "LoadStep":
                        combo.addItems(tableSetup.LoadSteps)
                    elif key == "ViewType":
                        combo.addItems(tableSetup.viewTypeOptions)
                        # Connect signal for ViewLabels combobox update and GridSystem state
                        def update_view_type(view_type, row, col):
                            # Update ViewLabels combobox
                            viewlabels_combo = self.mainTableWidget.cellWidget(row, col + 2)  # ViewLabels is 2 columns after ViewType
                            if viewlabels_combo:
                                viewlabels_combo.clear()
                                if view_type == "Story":
                                    viewlabels_combo.addItems(["Select all"] + tableSetup.StoryNames)
                                elif view_type == "Elevation":
                                    grid_system_combo = self.mainTableWidget.cellWidget(row, col + 1)  # GridSystem is next column
                                    if grid_system_combo:
                                        selected_grid = grid_system_combo.currentText()
                                        gridlines = next((list(grid.values())[0] for grid in tableSetup.GridSystemNames if list(grid.keys())[0] == selected_grid), [])
                                        viewlabels_combo.addItems(["Select all"] + gridlines)
                            
                            # Update GridSystem combobox state
                            grid_system_combo = self.mainTableWidget.cellWidget(row, col + 1)  # GridSystem is next column
                            if grid_system_combo:
                                if view_type == "Story":
                                    grid_system_combo.setEnabled(False)
                                    grid_system_combo.setCurrentText("")
                                else:  # Elevation
                                    grid_system_combo.setEnabled(True)
                        combo.currentTextChanged.connect(lambda text, r=row_idx, c=current_col: update_view_type(text, r, c))
                        # Set initial state
                        if value:
                            combo.setCurrentText(value)
                            update_view_type(value, row_idx, current_col)
                    elif key == "GridSystem":
                        combo.addItems([list(grid.keys())[0] for grid in tableSetup.GridSystemNames])
                        # Connect signal for ViewLabels combobox update when GridSystem changes
                        def update_viewlabels_grid(grid_system, row, col):
                            view_type_combo = self.mainTableWidget.cellWidget(row, col - 1)  # ViewType is previous column
                            if view_type_combo and view_type_combo.currentText() == "Elevation":
                                viewlabels_combo = self.mainTableWidget.cellWidget(row, col + 1)  # ViewLabels is next column
                                if viewlabels_combo:
                                    viewlabels_combo.clear()
                                    gridlines = next((list(grid.values())[0] for grid in tableSetup.GridSystemNames if list(grid.keys())[0] == grid_system), [])
                                    viewlabels_combo.addItems(["Select all"] + gridlines)
                        combo.currentTextChanged.connect(lambda text, r=row_idx, c=current_col: update_viewlabels_grid(text, r, c))
                        # Set initial enabled state based on ViewType
                        view_type_combo = self.mainTableWidget.cellWidget(row_idx, current_col - 1)  # ViewType is previous column
                        if view_type_combo:
                            combo.setEnabled(view_type_combo.currentText() == "Elevation")
                            if combo.isEnabled() and value:
                                combo.setCurrentText(value)
                                update_viewlabels_grid(value, row_idx, current_col)
                    elif key == "GroupName":
                        combo.addItems(tableSetup.GroupNames)
                    
                    combo.setCurrentText(str(value))
                    self.mainTableWidget.setCellWidget(row_idx, current_col, combo)
                elif widget_type == "spinbox":
                    spinbox = QtWidgets.QSpinBox()
                    spinbox.setValue(int(value))
                    self.mainTableWidget.setCellWidget(row_idx, current_col, spinbox)
                elif widget_type == "textEdit":
                    line_edit = QtWidgets.QLineEdit()
                    line_edit.setText(str(value))
                    self.mainTableWidget.setCellWidget(row_idx, current_col, line_edit)
                elif widget_type == "comboboxMultiple":
                    pass
                    
                current_col += 1
                
        # Make the table read-only (except for widgets)
        self.mainTableWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)