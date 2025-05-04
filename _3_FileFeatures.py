import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
import states.statesAllRequests as statesAllRequests
import database.tableSetup as tableSetup
import hooks.qtDesignerHooks as qtDesignerHooks
import json
import os
# Track the current open file
current_file = None

def update_window_title(main_window):
    global current_file
    if main_window:
        if current_file:
            main_window.inputFilePath.setText(current_file)
        else:
            main_window.inputFilePath.setText("")

def actionSave(main_window, mainTableWidget):
    """Save the current state to a JSON file"""
    global current_file
    if not current_file:
        return actionSaveAs(main_window, mainTableWidget)
    # Get the data from the UI
    data = {
        "outputFilePath": main_window.outputFilePath.toPlainText() if hasattr(main_window, 'outputFilePath') else "",
        "outputFolderPath": main_window.outputFolderPath.toPlainText() if hasattr(main_window, 'outputFolderPath') else "",
        "units": main_window.unitsComboBox.currentText() if hasattr(main_window, 'unitsComboBox') else "",
        "posViewTolerance": main_window.posViewToleranceSpinBox.value() if hasattr(main_window, 'posViewToleranceSpinBox') else 6,
        "negViewTolerance": main_window.negViewToleranceSpinBox.value() if hasattr(main_window, 'negViewToleranceSpinBox') else 6,
        "Requests": []
    }
    for row in range(3, mainTableWidget.rowCount()):
        request_data = {}
        for col, key in enumerate(tableSetup.RequestKeys):
            widget = mainTableWidget.cellWidget(row, col)
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
                container = widget
                label = container.findChild(QtWidgets.QLabel)
                if label:
                    request_data[key] = [item.strip() for item in label.text().split(',') if item.strip()]
                else:
                    request_data[key] = []
        data["Requests"].append(request_data)
    try:
        with open(current_file, 'w') as f:
            json.dump(data, f, indent=4)
        QtWidgets.QMessageBox.information(main_window, "Success", "File saved successfully!")
    except Exception as e:
        QtWidgets.QMessageBox.critical(main_window, "Error", f"Failed to save file: {str(e)}")

def actionSaveAs(main_window, mainTableWidget):
    """Save the current state to a new JSON file"""
    global current_file
    filename, _ = QtWidgets.QFileDialog.getSaveFileName(
        main_window,
        "Save File",
        "",
        "JSON Files (*.json);;All Files (*)"
    )
    if filename:
        current_file = filename
        actionSave(main_window, mainTableWidget)
        update_window_title(main_window)

def actionNew(main_window):
    """Create a new file, prompting to save current file if needed"""
    global current_file
    if not main_window:
        QtWidgets.QMessageBox.critical(None, "Error", "Could not access main window")
        return
    if current_file:
        reply = QtWidgets.QMessageBox.question(
            main_window,
            "New File",
            "Do you want to save changes to the current file?",
            QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel,
            QtWidgets.QMessageBox.Save
        )
        if reply == QtWidgets.QMessageBox.Save:
            actionSave(main_window, main_window.mainTableWidget)
        elif reply == QtWidgets.QMessageBox.Cancel:
            return
    current_file = None
    statesAllRequests.Requests = [statesAllRequests.defaultRow.copy()]
    if hasattr(main_window, 'outputFilePath'):
        main_window.outputFilePath.clear()
    if hasattr(main_window, 'outputFolderPath'):
        main_window.outputFolderPath.clear()
    if hasattr(main_window, 'unitsComboBox'):
        main_window.unitsComboBox.setCurrentIndex(0)
    if hasattr(main_window, 'posViewToleranceSpinBox'):
        main_window.posViewToleranceSpinBox.setValue(6)
    if hasattr(main_window, 'negViewToleranceSpinBox'):
        main_window.negViewToleranceSpinBox.setValue(6)
    main_window.mainTableWidget.setRowCount(3)
    main_window.MapRequestsToTable()
    update_window_title(main_window)

def actionOpen(main_window):
    """Open an existing JSON file"""
    global current_file
    if not main_window:
        QtWidgets.QMessageBox.critical(None, "Error", "Could not access main window")
        return
    if current_file:
        reply = QtWidgets.QMessageBox.question(
            main_window,
            "Open File",
            "Do you want to save changes to the current file?",
            QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel,
            QtWidgets.QMessageBox.Save
        )
        if reply == QtWidgets.QMessageBox.Save:
            actionSave(main_window, main_window.mainTableWidget)
        elif reply == QtWidgets.QMessageBox.Cancel:
            return
    filename, _ = QtWidgets.QFileDialog.getOpenFileName(
        main_window,
        "Open File",
        "",
        "JSON Files (*.json);;All Files (*)"
    )
    if filename:
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            current_file = filename
            if hasattr(main_window, 'outputFilePath'):
                main_window.outputFilePath.setText(data.get("outputFilePath", ""))
            if hasattr(main_window, 'outputFolderPath'):
                main_window.outputFolderPath.setText(data.get("outputFolderPath", ""))
            if hasattr(main_window, 'unitsComboBox'):
                index = main_window.unitsComboBox.findText(data.get("units", ""))
                if index >= 0:
                    main_window.unitsComboBox.setCurrentIndex(index)
            if hasattr(main_window, 'posViewToleranceSpinBox'):
                main_window.posViewToleranceSpinBox.setValue(data.get("posViewTolerance", 6))
            if hasattr(main_window, 'negViewToleranceSpinBox'):
                main_window.negViewToleranceSpinBox.setValue(data.get("negViewTolerance", 6))
            statesAllRequests.Requests = []
            for request_data in data.get("Requests", []):
                statesAllRequests.Requests.append(request_data)
            while main_window.mainTableWidget.rowCount() > 3:
                main_window.mainTableWidget.removeRow(3)
            for request in statesAllRequests.Requests:
                main_window.mainTableWidget.insertRow(main_window.mainTableWidget.rowCount())
            main_window.MapRequestsToTable()
            update_window_title(main_window)
            QtWidgets.QMessageBox.information(main_window, "Success", "File loaded successfully!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(main_window, "Error", f"Failed to load file: {str(e)}")