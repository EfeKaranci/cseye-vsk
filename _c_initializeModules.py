import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
import states.statesAllRequests as statesAllRequests
import database.tableSetup as tableSetup
import _e_WindowFeatures as _e_WindowFeatures
import _d_FileFeatures as _d_FileFeatures
import database.csiTables as csiTables
import Hooks.tableWidgetHooks as tableWidgetHooks

class ModulesScreen(QMainWindow):
    def __init__(self):
        super(ModulesScreen, self).__init__()
        loadUi("qtDesigner/windowModules.ui",self)
        self.setUnitsAndTolerances()
        self.setColumnsAndRows()
        self.setMainHeaders()
        self.helpIcons()
        self.setSubHeaders()
        self.MapRequestsToTable([statesAllRequests.defaultRow])
        
        self.modelPath.setText(statesAllRequests.modelPath)
        # Connect menu actions to file features
        self.actionNew.triggered.connect(lambda: _d_FileFeatures.actionNew(self))
        self.actionOpen.triggered.connect(lambda: _d_FileFeatures.actionOpen(self))
        self.actionSave.triggered.connect(lambda: _d_FileFeatures.actionSave(self, self.mainTableWidget))
        self.actionSaveAs.triggered.connect(lambda: _d_FileFeatures.actionSaveAs(self, self.mainTableWidget))
        
        # Connect button signals to window features
        self.newRowButton.clicked.connect(lambda: _e_WindowFeatures.newRow(self.mainTableWidget))
        self.deleteRowsButton.clicked.connect(lambda: _e_WindowFeatures.deleteRows(self.mainTableWidget))
        self.insertRowsBelowButton.clicked.connect(lambda: _e_WindowFeatures.insertRowsBelow(self.mainTableWidget))
        self.insertRowsAboveButton.clicked.connect(lambda: _e_WindowFeatures.insertRowsAbove(self.mainTableWidget))
        self.copyRowsButton.clicked.connect(lambda: _e_WindowFeatures.copyRows(self.mainTableWidget))
        self.runRequestsButton.clicked.connect(lambda: _e_WindowFeatures.runRequests(
            self.mainTableWidget,
            self.outputFilePath.toPlainText(),
            self.outputFolderPath.toPlainText(),
            self.unitsComboBox.currentText(),
            self.posViewToleranceSpinBox.value(),
            self.negViewToleranceSpinBox.value()
        ))

    def setUnitsAndTolerances(self):
        unitsOptions = list(csiTables.UnitsKey.keys())
        self.unitsComboBox.addItems(unitsOptions)
        self.posViewToleranceSpinBox.setValue(6)
        self.negViewToleranceSpinBox.setValue(6)

    def setColumnsAndRows(self):
        # Set the number of columns based on the total spans + 1 for checkbox column
        total_columns = sum(tableSetup.mainHeaderspans) + 1
        self.mainTableWidget.setColumnCount(total_columns)
        # Set the number of rows based on Requests length + 2 (1 for main headers, 1 for subheaders)
        self.mainTableWidget.setRowCount(4)
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
    
    def MapRequestsToTable(self,Requests):
        for i,request in enumerate(Requests, start=3):  # Start from row 2 (after headers)
            tableWidgetHooks.newRow(self.mainTableWidget,i,request)
