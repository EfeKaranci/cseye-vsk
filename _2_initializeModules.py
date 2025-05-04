import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QCheckBox, QListWidget
from PyQt5.QtCore import Qt, QEvent, QTimer
from PyQt5.QtGui import QStandardItem, QFontMetrics, QPalette
import states.statesAllRequests as statesAllRequests
import database.tableSetup as tableSetup
import hooks.csiHooks as csiHooks
import _3_WindowFeatures as _3_WindowFeatures
import hooks.qtDesignerHooks as qtDesignerHooks

class ModulesScreen(QMainWindow):
    def __init__(self):
        super(ModulesScreen, self).__init__()
        loadUi("qtDesigner/windowModules.ui",self)
        self.setColumnsAndRows()
        self.setMainHeaders()
        self.helpIcons()
        self.setSubHeaders()
        self.MapRequestsToTable()
        
        # Connect button signals to window features
        self.newRowButton.clicked.connect(lambda: _3_WindowFeatures.newRow(self.mainTableWidget))
        self.deleteRowsButton.clicked.connect(lambda: _3_WindowFeatures.deleteRows(self.mainTableWidget))
        self.insertRowsBelowButton.clicked.connect(lambda: _3_WindowFeatures.insertRowsBelow(self.mainTableWidget))
        self.insertRowsAboveButton.clicked.connect(lambda: _3_WindowFeatures.insertRowsAbove(self.mainTableWidget))
        self.copyRowsButton.clicked.connect(lambda: _3_WindowFeatures.copyRows(self.mainTableWidget))
        self.runRequestsButton.clicked.connect(lambda: _3_WindowFeatures.runRequests(self.mainTableWidget))

    def setColumnsAndRows(self):
        # Set the number of columns based on the total spans + 1 for checkbox column
        total_columns = sum(tableSetup.mainHeaderspans) + 1
        self.mainTableWidget.setColumnCount(total_columns)
        # Set the number of rows based on Requests length + 2 (1 for main headers, 1 for subheaders)
        self.mainTableWidget.setRowCount(len(statesAllRequests.Requests) + 3)
        # Hide the vertical header
        self.mainTableWidget.verticalHeader().setVisible(False)
        # Set table widget to expand and fill its container
        self.mainTableWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.mainTableWidget.horizontalHeader().setStretchLastSection(True)
        self.mainTableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # Set fixed width for checkbox column
        self.mainTableWidget.setColumnWidth(0, 30)  # 30 pixels wide for checkbox column

    def setMainHeaders(self):
        current_col = 0  # Start from column 1 to leave space for checkbox column
        for header, span in zip(tableSetup.mainHeaders, tableSetup.mainHeaderspans):
            item = QTableWidgetItem(header)
            self.mainTableWidget.setItem(0, current_col, item)
            self.mainTableWidget.setSpan(0, current_col, 1, span)
            current_col += span
    
    def helpIcons(self):
        # Create help icons for each subheader
        for col, subHeader in enumerate(tableSetup.subHeaders):
            if subHeader:  # Skip empty subheaders
                # Create container widget for help icon
                container = QtWidgets.QWidget()
                layout = QtWidgets.QHBoxLayout(container)
                layout.setContentsMargins(5, 0, 0, 0)  # Left margin to anchor to left
                layout.setSpacing(0)
                # Create help icon
                helpIcon = QtWidgets.QLabel("?")
                helpIcon.setFixedSize(20, 20)  # Fixed size for circle
                helpIcon.setStyleSheet("""
                    QLabel {background-color: #f0f0f0;border-radius: 10px;color: #000000;font-weight: bold;font-size: 12px;
                        padding: 0px;qproperty-alignment: AlignCenter;}
                    QLabel:hover {background-color: #e0e0e0;}
                """)
                helpIcon.setToolTip(tableSetup.helpTexts.get(subHeader, "No help text available"))
                # Add help icon to container
                layout.addWidget(helpIcon)
                # Set the container in the cell
                self.mainTableWidget.setCellWidget(1, col, container)
    
    def setSubHeaders(self):
        for i,header in enumerate(tableSetup.subHeaders):
            if i < len(tableSetup.subHeaders):
                item = QTableWidgetItem(header)
                self.mainTableWidget.setItem(2, i, item)
    
    def MapRequestsToTable(self):
        for i,request in enumerate(statesAllRequests.Requests, start=3):  # Start from row 2 (after headers)
            for j,key in enumerate(tableSetup.RequestKeys):
                if key == "Selected":
                    value = request.get(key, False)
                    checkbox = qtDesignerHooks.GetCheckbox(value)
                    self.mainTableWidget.setCellWidget(i, j, checkbox)
                elif key == "Run":
                    values = tableSetup.runOptions
                    combo = qtDesignerHooks.GetComboBox(values,request.get("Run", False))
                    self.mainTableWidget.setCellWidget(i, j, combo)
                elif key == "DataType":
                    values = list(tableSetup.dataOptions.keys())
                    combo = qtDesignerHooks.GetComboBox(values,request.get("DataType", False))
                    self.mainTableWidget.setCellWidget(i, j, combo)
                    combo.currentTextChanged.connect(lambda text, row=i, col=j: self.handleDataTypeChange(text, row, col))
                elif key == "Data":
                    values = tableSetup.dataOptions[request.get("DataType", False)]
                    combo = qtDesignerHooks.GetComboBox(values,request.get("Data", False))
                    self.mainTableWidget.setCellWidget(i, j, combo)
                elif key == "LoadCase":
                    values = tableSetup.LoadCombinationNames
                    combo = qtDesignerHooks.GetComboBox(values,request.get("LoadCase", False))
                    self.mainTableWidget.setCellWidget(i, j, combo)
                elif key == "LoadStep":
                    values = tableSetup.LoadSteps
                    combo = qtDesignerHooks.GetComboBox(values,request.get("LoadStep", False))
                    self.mainTableWidget.setCellWidget(i, j, combo)
                elif key == "ViewType":
                    values = tableSetup.viewTypeOptions
                    combo = qtDesignerHooks.GetComboBox(values,request.get("ViewType", False))
                    self.mainTableWidget.setCellWidget(i, j, combo)
                    combo.currentTextChanged.connect(lambda text, row=i, col=j: self.handleViewTypeChange(text, row, col))
                elif key == "GridSystem":
                    values = [list(grid.keys())[0] for grid in tableSetup.GridSystemNames]
                    combo = qtDesignerHooks.GetComboBox(values,request.get("GridSystem", False))
                    self.mainTableWidget.setCellWidget(i, j, combo)
                elif key == "ViewLabels":
                    print(request.get("ViewLabels"))
                    values = request.get("ViewLabels", [])
                    valuesString =', '.join(map(str, values))
                    container = qtDesignerHooks.GetLabelAndButton(valuesString, i, j, self.mainTableWidget)
                    self.mainTableWidget.setCellWidget(i, j, container)
                elif key == "GroupName":
                    values = tableSetup.GroupNames
                    combo = qtDesignerHooks.GetComboBox(values,request.get("GroupName", False))
                    self.mainTableWidget.setCellWidget(i, j, combo)
                elif key == "DecimalPlaces":
                    spinbox = qtDesignerHooks.GetSpinBox(request.get("DecimalPlaces", False))
                    self.mainTableWidget.setCellWidget(i, j, spinbox)
                elif key == "TextScale":
                    spinbox = qtDesignerHooks.GetSpinBox(request.get("TextScale", False))
                    self.mainTableWidget.setCellWidget(i, j, spinbox)
                elif key == "MarkerScale":
                    spinbox = qtDesignerHooks.GetSpinBox(request.get("MarkerScale", False))
                    self.mainTableWidget.setCellWidget(i, j, spinbox)
                elif key == "OutputPdf":
                    checkbox = qtDesignerHooks.GetCheckbox(request.get("OutputPdf", False))
                    self.mainTableWidget.setCellWidget(i, j, checkbox)
                elif key == "OutputExcel":
                    checkbox = qtDesignerHooks.GetCheckbox(request.get("OutputExcel", False))
                    self.mainTableWidget.setCellWidget(i, j, checkbox)

    def handleDataTypeChange(self,data_type,row,col):
        if data_type in tableSetup.dataOptions:
            values = tableSetup.dataOptions[data_type]
            value = tableSetup.dataOptions[data_type][0]
            combo = qtDesignerHooks.GetComboBox(values,value)
            self.mainTableWidget.setCellWidget(row, col+1, combo)
            #Function to handle specific data types...
            #Data types for Stories only
            #Data types with no load needed
            #Data types that run on all stories
            #Data types with some formatting disabled
            #data types with no pdf/excel output
    
    def handleViewTypeChange(self, viewType, row, col):
        # Get the grid system combo box from the next column
        gridSystemCombo = self.mainTableWidget.cellWidget(row, col + 1)
        if gridSystemCombo:
            if viewType == "Story":
                gridSystemCombo.setEnabled(False)
                gridSystemCombo.setCurrentText("")
            else:  # Elevation
                gridSystemCombo.setEnabled(True)
        # Clear the view labels for this row
        viewLabelsCol = tableSetup.RequestKeys.index("ViewLabels")
        request = statesAllRequests.Requests[row - 3]  # Adjust for header rows
        request["ViewLabels"] = []
        # Update the UI to show empty view labels
        container = qtDesignerHooks.GetLabelAndButton("", row, viewLabelsCol, self.mainTableWidget)
        self.mainTableWidget.setCellWidget(row, viewLabelsCol, container)

class ViewSelectionDialog(QtWidgets.QDialog):
    def __init__(self, viewType, gridSystem, currentLabels, parent=None):
        super(ViewSelectionDialog, self).__init__(parent)
        loadUi("qtDesigner/windowSelectViews.ui", self)
        # Set the label text based on view type
        self.ViewsTypeLabel.setText("Select stories" if viewType == "Story" else "Select elevations")
        # Create a scroll area for the checkboxes
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setMinimumHeight(200)
        # Create a container widget for the checkboxes
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        # Add "Select All" checkbox
        selectAll = QtWidgets.QCheckBox("Select All")
        selectAll.stateChanged.connect(lambda state: self.toggle_all_checkboxes(state))
        layout.addWidget(selectAll)
        # Add checkboxes based on view type
        self.checkboxes = []
        if viewType == "Story":
            items = tableSetup.StoryNames
        else:  # Elevation
            gridDict = next((grid for grid in tableSetup.GridSystemNames if list(grid.keys())[0] == gridSystem), None)
            items = list(gridDict.values())[0] if gridDict else []
        
        # Check if all items are selected for the "Select All" checkbox
        allSelected = len(items) > 0 and all(item in currentLabels for item in items)
        selectAll.setChecked(allSelected)
        
        for item in items:
            checkbox = QtWidgets.QCheckBox(item)
            checkbox.setChecked(item in currentLabels)
            self.checkboxes.append(checkbox)
            layout.addWidget(checkbox)
        
        # Add the container to the scroll area
        scrollArea.setWidget(container)
        
        # Add the scroll area to the dialog's layout
        self.verticalLayout2.addWidget(scrollArea)
        
        # Connect the save button
        self.SaveViewButton.clicked.connect(self.save_selection)
        
        # Store the current labels for comparison
        self.currentLabels = currentLabels
        self.selected_labels = currentLabels.copy()  # Initialize with current labels
    
    def toggle_all_checkboxes(self, state):
        for checkbox in self.checkboxes:
            checkbox.setChecked(state == Qt.Checked)
    
    def save_selection(self):
        self.selected_labels = [checkbox.text() for checkbox in self.checkboxes if checkbox.isChecked()]
        self.accept()