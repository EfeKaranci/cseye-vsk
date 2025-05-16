import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
import states.statesAllRequests as statesAllRequests
import database.tableSetup as tableSetup
import Hooks.qtDesignerHooks as qtDesignerHooks
import _f_ProcessRequests as _f_ProcessRequests
import Hooks.viewLabelsDialogHook as viewLabelsDialogHook
def newRow(table_widget,rowIndex,rowData):
    for j,key in enumerate(tableSetup.RequestKeys):
            value = rowData.get(key, False)
            if key == "Selected":
                checkbox = qtDesignerHooks.GetCheckbox(value)
                table_widget.setCellWidget(rowIndex, j, checkbox)
            elif key == "Run":
                values = tableSetup.runOptions
                combo = qtDesignerHooks.GetComboBox(values,value)
                table_widget.setCellWidget(rowIndex, j, combo)
            elif key == "DataType":
                dataOptions = list(tableSetup.dataOptions.keys())
                dataOptions.sort()
                values = dataOptions
                combo = qtDesignerHooks.GetComboBox(values,value)
                table_widget.setCellWidget(rowIndex, j, combo)
                combo.currentTextChanged.connect(lambda text, row=rowIndex, col=j: handleDataTypeChange(table_widget,text, row, col))
            elif key == "Data":
                values = tableSetup.dataOptions[rowData.get("DataType", False)]
                combo = qtDesignerHooks.GetComboBox(values,value)
                table_widget.setCellWidget(rowIndex, j, combo)
            elif key == "LoadCase":
                values = tableSetup.LoadCombinationNames
                combo = qtDesignerHooks.GetComboBox(values,value)
                if rowData.get("DataType") in tableSetup.DataThatDoNotRequireRunModel or rowData.get("DataType") in tableSetup.DataWithNoLoads:
                    combo.setCurrentText("")
                    combo.setEnabled(False)
                table_widget.setCellWidget(rowIndex, j, combo)
            elif key == "LoadStep":
                values = tableSetup.LoadSteps
                combo = qtDesignerHooks.GetComboBox(values,value)
                if rowData.get("DataType") in tableSetup.DataThatDoNotRequireRunModel or rowData.get("DataType") in tableSetup.DataWithNoLoads:
                    combo.setCurrentText("")
                    combo.setEnabled(False)
                table_widget.setCellWidget(rowIndex, j, combo)
            elif key == "ViewType":
                values = tableSetup.viewTypeOptions
                combo = qtDesignerHooks.GetComboBox(values,value)
                if (rowData.get("DataType") in tableSetup.DataForStoryViewOnly) or (rowData.get("DataType") in tableSetup.DataWithExcelOnly):
                    combo.setCurrentText("Story")
                    combo.setEnabled(False)
                table_widget.setCellWidget(rowIndex, j, combo)
                combo.currentTextChanged.connect(lambda text, row=rowIndex, col=j: handleViewTypeChange(table_widget,text, row, col))
            elif key == "GridSystem":
                values = [list(grid.keys())[0] for grid in tableSetup.GridSystemNames]
                combo = qtDesignerHooks.GetComboBox(values,value)
                if (rowData.get("ViewType") == "Story") or (rowData.get("DataType") in tableSetup.DataWithExcelOnly):
                    combo.setEnabled(False)
                table_widget.setCellWidget(rowIndex, j, combo)
            elif key == "ViewLabels":
                values = rowData.get("ViewLabels", [])
                valuesString =', '.join(map(str, values))
                container = viewLabelsDialogHook.GetLabelAndButton(valuesString, rowIndex, j, table_widget,rowData)
                table_widget.setCellWidget(rowIndex, j, container)
            elif key == "GroupName":
                values = tableSetup.GroupNames
                combo = qtDesignerHooks.GetComboBox(values,value)
                if (rowData.get("DataType") in tableSetup.DataWithExcelOnly):
                    combo.setEnabled(False)
                table_widget.setCellWidget(rowIndex, j, combo)
            elif key == "DecimalPlaces":
                spinbox = qtDesignerHooks.GetSpinBox(value)
                if (rowData.get("DataType") in tableSetup.DatawithNoDecimalPlaces) or (rowData.get("DataType") in tableSetup.DataWithExcelOnly):
                    spinbox.setValue(0)
                    spinbox.setEnabled(False)
                table_widget.setCellWidget(rowIndex, j, spinbox)
            elif key == "TextScale":
                spinbox = qtDesignerHooks.GetSpinBox(value)
                if (rowData.get("DataType") in tableSetup.DataWithExcelOnly):
                    spinbox.setEnabled(False)
                table_widget.setCellWidget(rowIndex, j, spinbox)
            elif key == "MarkerScale":
                spinbox = qtDesignerHooks.GetSpinBox(value)
                if (rowData.get("DataType") in tableSetup.DataWithNoMarkers) or (rowData.get("DataType") in tableSetup.DataWithExcelOnly):
                    spinbox.setValue(0)
                    spinbox.setEnabled(False)
                table_widget.setCellWidget(rowIndex, j, spinbox)
            elif key == "OutputPdf":
                checkbox = qtDesignerHooks.GetCheckbox(value)
                if (rowData.get("DataType") in tableSetup.DataWithNoPdf) or (rowData.get("DataType") in tableSetup.DataWithExcelOnly):
                    checkbox.setChecked(False)
                    checkbox.setEnabled(False)
                table_widget.setCellWidget(rowIndex, j, checkbox)
            elif key == "OutputExcel":
                checkbox = qtDesignerHooks.GetCheckbox(value)
                if (rowData.get("DataType") in tableSetup.DataWithExcelOnly):
                    checkbox.setChecked(True)
                    checkbox.setEnabled(False)
                if rowData.get("DataType") in tableSetup.DataWithNoExcel:
                    checkbox.setChecked(False)
                    checkbox.setEnabled(False)
                table_widget.setCellWidget(rowIndex, j, checkbox)


def handleDataTypeChange(table_widget,data_type,row,col):
    if data_type in tableSetup.dataOptions:
        values = tableSetup.dataOptions[data_type]
        value = tableSetup.dataOptions[data_type][0]
        combo = qtDesignerHooks.GetComboBox(values,value)
        table_widget.setCellWidget(row, col+1, combo)
        def dataTypeChange1(table_widget,row,col):
            loadCaseCombo = table_widget.cellWidget(row, col+2)
            loadStepCombo = table_widget.cellWidget(row, col+3)
            if data_type in tableSetup.DataThatDoNotRequireRunModel or data_type in tableSetup.DataWithNoLoads:
                loadCaseCombo.setCurrentText("")
                loadCaseCombo.setEnabled(False)
                loadStepCombo.setCurrentText("")
                loadStepCombo.setEnabled(False)
            else:
                loadCaseCombo.setEnabled(True)
                loadStepCombo.setEnabled(True)
        def dataTypeChange2(table_widget,row,col):
            markerScaleSpinBox = table_widget.cellWidget(row, col+10)
            if data_type in tableSetup.DataWithNoMarkers:
                markerScaleSpinBox.setValue(1)
                markerScaleSpinBox.setEnabled(False)
            else:
                markerScaleSpinBox.setValue(1)
                markerScaleSpinBox.setEnabled(True)
        def dataTypeChange3(table_widget,row,col):
            decimalPlacesSpinBox = table_widget.cellWidget(row, col+8)
            if data_type in tableSetup.DatawithNoDecimalPlaces:
                decimalPlacesSpinBox.setValue(1)
                decimalPlacesSpinBox.setEnabled(False)
            else:
                decimalPlacesSpinBox.setValue(1)
                decimalPlacesSpinBox.setEnabled(True)
        def dataTypeChange4(table_widget,row,col):
            viewTypeCombo = table_widget.cellWidget(row, col+4)
            gridSystemCombo = table_widget.cellWidget(row, col+5)
            if data_type in tableSetup.DataForStoryViewOnly:
                viewTypeCombo.setCurrentText("Story")
                viewTypeCombo.setEnabled(False)
                gridSystemCombo.setEnabled(False)
            else:
                viewTypeCombo.setEnabled(True)
                gridSystemCombo.setEnabled(True)
        def dataTypeChange5(table_widget,row,col):
            outputPdfCheckbox = table_widget.cellWidget(row, col+11)
            if data_type in tableSetup.DataWithNoPdf:
                outputPdfCheckbox.setChecked(False)
                outputPdfCheckbox.setEnabled(False)
            else:
                outputPdfCheckbox.setChecked(True)
                outputPdfCheckbox.setEnabled(True)
        def dataTypeChange6(table_widget,row,col):
            outputExcelCheckbox = table_widget.cellWidget(row, col+12)
            if data_type in tableSetup.DataWithNoExcel:
                outputExcelCheckbox.setChecked(False)
                outputExcelCheckbox.setEnabled(False)
            else:
                outputExcelCheckbox.setChecked(True)
                outputExcelCheckbox.setEnabled(True)
        def dataTypeChange7(table_widget,row,col):
            outputExcelCheckbox = table_widget.cellWidget(row, col+12)
            if data_type in tableSetup.DataWithExcelOnly:
                outputExcelCheckbox.setChecked(True)
                outputExcelCheckbox.setEnabled(True)
        def dataTypeChange8(table_widget,row,col):
            textScaleSpinBox = table_widget.cellWidget(row, col+9)
            if data_type in tableSetup.DataWithNoText:
                textScaleSpinBox.setValue(1)
                textScaleSpinBox.setEnabled(False)
            else:
                textScaleSpinBox.setEnabled(True)
        dataTypeChange1(table_widget,row,col)
        dataTypeChange2(table_widget,row,col)
        dataTypeChange3(table_widget,row,col)   
        dataTypeChange4(table_widget,row,col)
        dataTypeChange5(table_widget,row,col)
        dataTypeChange6(table_widget,row,col)
        dataTypeChange7(table_widget,row,col)
        dataTypeChange8(table_widget,row,col)
        #data types with no pdf/excel output
    
def handleViewTypeChange(table_widget, viewType, row, col):
    # Get the grid system combo box from the next column
    gridSystemCombo = table_widget.cellWidget(row, col + 1)
    if gridSystemCombo:
        if viewType == "Story":
            gridSystemCombo.setEnabled(False)
            gridSystemCombo.setCurrentText("")
        else:  # Elevation
            gridSystemCombo.setEnabled(True)
    # Clear the view labels for this row
    viewLabelsCol = tableSetup.RequestKeys.index("ViewLabels")
    rowData = getTableRowData(table_widget,row)  # Adjust for header rows
    rowData["ViewLabels"] = []
    # Update the UI to show empty view labels
    container = viewLabelsDialogHook.GetLabelAndButton("", row, viewLabelsCol, table_widget,rowData)
    table_widget.setCellWidget(row, viewLabelsCol, container)

def getTableRequests(table_widget,Key,Value):
    selected_requests = []
    selected_Indices= []
    # Iterate through all rows (skipping header rows)
    for rowIndex in range(3, table_widget.rowCount()):
        # Check if rowIndex is selected
        selected_col = tableSetup.RequestKeys.index(Key)
        ValueWidget = table_widget.cellWidget(rowIndex, selected_col)
        if (Key == "Selected" and ValueWidget.isChecked()) or (Key != "Selected" and ValueWidget.currentText() == Value):
            request_data = {}
            # Get data from each column
            for j, key in enumerate(tableSetup.RequestKeys):
                widget = table_widget.cellWidget(rowIndex, j)
                if not widget:
                    continue
                if key == "Selected":
                    request_data[key] = widget.isChecked()
                elif key in ["Run", "DataType", "Data", "LoadCase", "LoadStep", "ViewType", "GridSystem", "GroupName"]:
                    request_data[key] = widget.currentText()
                elif key in ["DecimalPlaces", "TextScale", "MarkerScale"]:
                    request_data[key] = widget.value()
                elif key in ["OutputPdf", "OutputExcel"]:
                    request_data[key] = widget.isChecked()
                elif key == "ViewLabels":
                    # Get the label text from the container widget
                    container = widget
                    label = container.findChild(QtWidgets.QLabel)
                    if label:
                        # Split the comma-separated string into a list
                        request_data[key] = [item.strip() for item in label.text().split(',') if item.strip()]
                    else:
                        request_data[key] = []
            
            # Add the rowData to our list
            selected_requests.append(request_data)
            selected_Indices.append(rowIndex)
    return selected_requests, selected_Indices

def getTableRowData(table_widget,rowIndex):
    rowData = {}
    for columnIndex, key in enumerate(tableSetup.RequestKeys):
        widget = table_widget.cellWidget(rowIndex, columnIndex)
        if widget:
            if key in ["Selected", "OutputPdf", "OutputExcel"]:
                rowData[key] = widget.isChecked()
            elif key in ["Run", "DataType", "Data", "LoadCase", "LoadStep", "ViewType", "GridSystem", "GroupName"]:
                rowData[key] = widget.currentText() 
            elif key in ["DecimalPlaces", "TextScale", "MarkerScale"]:
                rowData[key] = widget.value()
            elif key == "ViewLabels":
                # Find the QLabel child widget within the container
                label = widget.findChild(QtWidgets.QLabel)
                if label:
                    # Split the text using | as delimiter and strip whitespace
                    rowData[key] = [item.strip() for item in label.text().split(';') if item.strip()]
                else:
                    rowData[key] = []
    return rowData