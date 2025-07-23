import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
import states.statesAllRequests as statesAllRequests
import database.tableSetup as tableSetup
import hooks.qtDesignerHooks as qtDesignerHooks
import json
import os
import hooks.basicHooks as BasicHooks
import states.statesAllRequests as statesAllRequests
# Track the current open file
current_file = None

def update_window_title(main_window):
    global current_file
    if main_window:
        if current_file:
            main_window.ui.inputFilePath.setText(current_file)
        else:
            main_window.ui.inputFilePath.setText("")

def create_styled_message_box(parent, title, message, buttons=None, default_button=None):
    """Create a styled message box with wider buttons"""
    msg_box = QtWidgets.QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    
    if buttons:
        msg_box.setStandardButtons(buttons)
        if default_button:
            msg_box.setDefaultButton(default_button)
    
    # Set minimum width for all buttons
    for button in msg_box.buttons():
        button.setMinimumWidth(100)
        button.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
    
    return msg_box

def actionSave(main_window, mainTableWidget):
    """Save the current state to a JSON file"""
    global current_file
    if not main_window:
        msg_box = create_styled_message_box(None, "Error", "Could not access main window")
        msg_box.exec_()
        return
    if not current_file:
        return actionSaveAs(main_window, mainTableWidget)
    # Get the data from the UI
    data = {
        "outputFilePath": main_window.ui.outputFilePath.toPlainText() if hasattr(main_window.ui, 'outputFilePath') else "",
        "outputFolderPath": main_window.ui.outputFolderPath.toPlainText() if hasattr(main_window.ui, 'outputFolderPath') else "",
        "units": main_window.ui.unitsComboBox.currentText() if hasattr(main_window.ui, 'unitsComboBox') else "",
        "posViewTolerance": main_window.ui.posViewToleranceSpinBox.value() if hasattr(main_window.ui, 'posViewToleranceSpinBox') else 6,
        "negViewTolerance": main_window.ui.negViewToleranceSpinBox.value() if hasattr(main_window.ui, 'negViewToleranceSpinBox') else 6,
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
        msg_box = create_styled_message_box(main_window, "Success", "File saved successfully!")
        msg_box.exec_()
    except Exception as e:
        msg_box = create_styled_message_box(main_window, "Error", f"Failed to save file: {str(e)}")
        msg_box.exec_()

def actionSaveAs(main_window, mainTableWidget):
    """Save the current state to a new JSON file"""
    global current_file
    filename, _ = QtWidgets.QFileDialog.getSaveFileName(
        main_window.centralWidget().window(),  # Use the actual window widget as parent
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
        msg_box = create_styled_message_box(None, "Error", "Could not access main window")
        msg_box.exec_()
        return
    if current_file:
        msg_box = create_styled_message_box(
            main_window,
            "New File",
            "Do you want to save changes to the current file?",
            QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel,
            QtWidgets.QMessageBox.Save
        )
        reply = msg_box.exec_()
        if reply == QtWidgets.QMessageBox.Save:
            actionSave(main_window, main_window.ui.mainTableWidget)
        elif reply == QtWidgets.QMessageBox.Cancel:
            return
    current_file = None
    BasicHooks.resetDefaultRow()
    if hasattr(main_window.ui, 'outputFilePath'):
        main_window.ui.outputFilePath.clear()
    if hasattr(main_window.ui, 'outputFolderPath'):
        main_window.ui.outputFolderPath.clear()
    if hasattr(main_window.ui, 'unitsComboBox'):
        main_window.ui.unitsComboBox.setCurrentIndex(0)
    if hasattr(main_window.ui, 'posViewToleranceSpinBox'):
        main_window.ui.posViewToleranceSpinBox.setValue(6)
    if hasattr(main_window.ui, 'negViewToleranceSpinBox'):
        main_window.ui.negViewToleranceSpinBox.setValue(6)
    main_window.ui.mainTableWidget.setRowCount(3)
    BasicHooks.resetDefaultRow()
    main_window.MapRequestsToTable([statesAllRequests.defaultRow])
    update_window_title(main_window)

def actionOpen(main_window):
    """Open an existing JSON file"""
    global current_file
    if not main_window:
        msg_box = create_styled_message_box(None, "Error", "Could not access main window")
        msg_box.exec_()
        return
    if current_file:
        msg_box = create_styled_message_box(
            main_window,
            "Open File",
            "Do you want to save changes to the current file?",
            QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel,
            QtWidgets.QMessageBox.Save
        )
        reply = msg_box.exec_()
        
        if reply == QtWidgets.QMessageBox.Save:
            actionSave(main_window, main_window.ui.mainTableWidget)
        elif reply == QtWidgets.QMessageBox.Cancel:
            return
    
    filename, _ = QtWidgets.QFileDialog.getOpenFileName(
        main_window.centralWidget().window(),  # Use the actual window widget as parent
        "Open JSON File",
        "",
        "JSON Files (*.json);;All Files (*)"
    )
    
    if filename:
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            current_file = filename
            if hasattr(main_window.ui, 'outputFilePath'):
                main_window.ui.outputFilePath.setText(data.get("outputFilePath", ""))
            if hasattr(main_window.ui, 'outputFolderPath'):
                main_window.ui.outputFolderPath.setText(data.get("outputFolderPath", ""))
            if hasattr(main_window.ui, 'unitsComboBox'):
                index = main_window.ui.unitsComboBox.findText(data.get("units", ""))
                if index >= 0:
                    main_window.ui.unitsComboBox.setCurrentIndex(index)
            if hasattr(main_window.ui, 'posViewToleranceSpinBox'):
                main_window.ui.posViewToleranceSpinBox.setValue(data.get("posViewTolerance", 6))
            if hasattr(main_window.ui, 'negViewToleranceSpinBox'):
                main_window.ui.negViewToleranceSpinBox.setValue(data.get("negViewTolerance", 6))
            Requests = []
            while main_window.ui.mainTableWidget.rowCount() > 3:
                main_window.ui.mainTableWidget.removeRow(3)
            for request_data in data.get("Requests", []):
                Requests.append(request_data)
                main_window.ui.mainTableWidget.insertRow(main_window.ui.mainTableWidget.rowCount())
            main_window.MapRequestsToTable(Requests)
            update_window_title(main_window)
            msg_box = create_styled_message_box(main_window, "Success", "File loaded successfully!")
            msg_box.exec_()
        except Exception as e:
            msg_box = create_styled_message_box(main_window, "Error", f"Failed to load file: {str(e)}")
            msg_box.exec_()