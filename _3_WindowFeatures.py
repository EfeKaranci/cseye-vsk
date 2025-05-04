import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
import states.statesAllRequests as statesAllRequests
import database.tableSetup as tableSetup
import hooks.qtDesignerHooks as qtDesignerHooks

def newRow(table_widget):
    """Add a new row to the table with default values"""
    # Get the current number of rows
    current_row = table_widget.rowCount()
    
    # Add a new row
    table_widget.insertRow(current_row)
    
    # Create a new request with default values
    new_request = statesAllRequests.defaultRow.copy()
    statesAllRequests.Requests.append(new_request)
    
    # Map the new request to the table
    for j, key in enumerate(tableSetup.RequestKeys):
        if key == "Selected":
            checkbox = qtDesignerHooks.GetCheckbox(False)
            table_widget.setCellWidget(current_row, j, checkbox)
        elif key == "Run":
            combo = qtDesignerHooks.GetComboBox(tableSetup.runOptions, False)
            table_widget.setCellWidget(current_row, j, combo)
        elif key == "DataType":
            combo = qtDesignerHooks.GetComboBox(list(tableSetup.dataOptions.keys()), False)
            table_widget.setCellWidget(current_row, j, combo)
        elif key == "Data":
            combo = qtDesignerHooks.GetComboBox([], False)
            table_widget.setCellWidget(current_row, j, combo)
        elif key == "LoadCase":
            combo = qtDesignerHooks.GetComboBox(tableSetup.LoadCombinationNames, False)
            table_widget.setCellWidget(current_row, j, combo)
        elif key == "LoadStep":
            combo = qtDesignerHooks.GetComboBox(tableSetup.LoadSteps, False)
            table_widget.setCellWidget(current_row, j, combo)
        elif key == "ViewType":
            combo = qtDesignerHooks.GetComboBox(tableSetup.viewTypeOptions, False)
            table_widget.setCellWidget(current_row, j, combo)
        elif key == "GridSystem":
            combo = qtDesignerHooks.GetComboBox([list(grid.keys())[0] for grid in tableSetup.GridSystemNames], False)
            table_widget.setCellWidget(current_row, j, combo)
        elif key == "ViewLabels":
            container = qtDesignerHooks.GetLabelAndButton("", current_row, j, table_widget)
            table_widget.setCellWidget(current_row, j, container)
        elif key == "GroupName":
            combo = qtDesignerHooks.GetComboBox(tableSetup.GroupNames, False)
            table_widget.setCellWidget(current_row, j, combo)
        elif key == "DecimalPlaces":
            spinbox = qtDesignerHooks.GetSpinBox(0)
            table_widget.setCellWidget(current_row, j, spinbox)
        elif key == "TextScale":
            spinbox = qtDesignerHooks.GetSpinBox(0)
            table_widget.setCellWidget(current_row, j, spinbox)
        elif key == "MarkerScale":
            spinbox = qtDesignerHooks.GetSpinBox(0)
            table_widget.setCellWidget(current_row, j, spinbox)
        elif key == "OutputPdf":
            checkbox = qtDesignerHooks.GetCheckbox(False)
            table_widget.setCellWidget(current_row, j, checkbox)
        elif key == "OutputExcel":
            checkbox = qtDesignerHooks.GetCheckbox(False)
            table_widget.setCellWidget(current_row, j, checkbox)

def deleteRows(table_widget):
    """Delete selected rows from the table"""
    # Get rows where "Selected" is checked
    selected_rows = []
    for row in range(3, table_widget.rowCount()):  # Start from row 3 to skip headers
        selected_col = tableSetup.RequestKeys.index("Selected")
        checkbox = table_widget.cellWidget(row, selected_col)
        if checkbox and checkbox.isChecked():
            selected_rows.append(row)
    
    # Sort rows in descending order to avoid index shifting
    for row in sorted(selected_rows, reverse=True):
        table_widget.removeRow(row)
        # Adjust the index for the Requests array (subtract 3 for header rows)
        del statesAllRequests.Requests[row - 3]

def insertRowsBelow(table_widget):
    """Insert a new row below the selected row"""
    # Get the last row where "Selected" is checked
    selected_row = None
    for row in range(3, table_widget.rowCount()):  # Start from row 3 to skip headers
        selected_col = tableSetup.RequestKeys.index("Selected")
        checkbox = table_widget.cellWidget(row, selected_col)
        if checkbox and checkbox.isChecked():
            selected_row = row
    
    if selected_row is None:
        return
    
    # Insert row in the table
    table_widget.insertRow(selected_row + 1)
    
    # Create a new request with default values
    new_request = statesAllRequests.defaultRow.copy()
    # Insert at the correct position in Requests array (subtract 3 for header rows)
    statesAllRequests.Requests.insert(selected_row - 2, new_request)
    
    # Map the new request to the table
    for j, key in enumerate(tableSetup.RequestKeys):
        if key == "Selected":
            checkbox = qtDesignerHooks.GetCheckbox(False)
            table_widget.setCellWidget(selected_row + 1, j, checkbox)
        elif key == "Run":
            combo = qtDesignerHooks.GetComboBox(tableSetup.runOptions, False)
            table_widget.setCellWidget(selected_row + 1, j, combo)
        elif key == "DataType":
            combo = qtDesignerHooks.GetComboBox(list(tableSetup.dataOptions.keys()), False)
            table_widget.setCellWidget(selected_row + 1, j, combo)
        elif key == "Data":
            combo = qtDesignerHooks.GetComboBox([], False)
            table_widget.setCellWidget(selected_row + 1, j, combo)
        elif key == "LoadCase":
            combo = qtDesignerHooks.GetComboBox(tableSetup.LoadCombinationNames, False)
            table_widget.setCellWidget(selected_row + 1, j, combo)
        elif key == "LoadStep":
            combo = qtDesignerHooks.GetComboBox(tableSetup.LoadSteps, False)
            table_widget.setCellWidget(selected_row + 1, j, combo)
        elif key == "ViewType":
            combo = qtDesignerHooks.GetComboBox(tableSetup.viewTypeOptions, False)
            table_widget.setCellWidget(selected_row + 1, j, combo)
        elif key == "GridSystem":
            combo = qtDesignerHooks.GetComboBox([list(grid.keys())[0] for grid in tableSetup.GridSystemNames], False)
            table_widget.setCellWidget(selected_row + 1, j, combo)
        elif key == "ViewLabels":
            container = qtDesignerHooks.GetLabelAndButton("", selected_row + 1, j, table_widget)
            table_widget.setCellWidget(selected_row + 1, j, container)
        elif key == "GroupName":
            combo = qtDesignerHooks.GetComboBox(tableSetup.GroupNames, False)
            table_widget.setCellWidget(selected_row + 1, j, combo)
        elif key == "DecimalPlaces":
            spinbox = qtDesignerHooks.GetSpinBox(0)
            table_widget.setCellWidget(selected_row + 1, j, spinbox)
        elif key == "TextScale":
            spinbox = qtDesignerHooks.GetSpinBox(0)
            table_widget.setCellWidget(selected_row + 1, j, spinbox)
        elif key == "MarkerScale":
            spinbox = qtDesignerHooks.GetSpinBox(0)
            table_widget.setCellWidget(selected_row + 1, j, spinbox)
        elif key == "OutputPdf":
            checkbox = qtDesignerHooks.GetCheckbox(False)
            table_widget.setCellWidget(selected_row + 1, j, checkbox)
        elif key == "OutputExcel":
            checkbox = qtDesignerHooks.GetCheckbox(False)
            table_widget.setCellWidget(selected_row + 1, j, checkbox)

def insertRowsAbove(table_widget):
    """Insert a new row above the selected row"""
    # Get the first row where "Selected" is checked
    selected_row = None
    for row in range(3, table_widget.rowCount()):  # Start from row 3 to skip headers
        selected_col = tableSetup.RequestKeys.index("Selected")
        checkbox = table_widget.cellWidget(row, selected_col)
        if checkbox and checkbox.isChecked():
            selected_row = row
            break  # We only need the first selected row
    
    if selected_row is None:
        return
    
    # Insert row in the table
    table_widget.insertRow(selected_row)
    
    # Create a new request with default values
    new_request = statesAllRequests.defaultRow.copy()
    # Insert at the correct position in Requests array (subtract 3 for header rows)
    statesAllRequests.Requests.insert(selected_row - 3, new_request)
    
    # Map the new request to the table
    for j, key in enumerate(tableSetup.RequestKeys):
        if key == "Selected":
            checkbox = qtDesignerHooks.GetCheckbox(False)
            table_widget.setCellWidget(selected_row, j, checkbox)
        elif key == "Run":
            combo = qtDesignerHooks.GetComboBox(tableSetup.runOptions, False)
            table_widget.setCellWidget(selected_row, j, combo)
        elif key == "DataType":
            combo = qtDesignerHooks.GetComboBox(list(tableSetup.dataOptions.keys()), False)
            table_widget.setCellWidget(selected_row, j, combo)
        elif key == "Data":
            combo = qtDesignerHooks.GetComboBox([], False)
            table_widget.setCellWidget(selected_row, j, combo)
        elif key == "LoadCase":
            combo = qtDesignerHooks.GetComboBox(tableSetup.LoadCombinationNames, False)
            table_widget.setCellWidget(selected_row, j, combo)
        elif key == "LoadStep":
            combo = qtDesignerHooks.GetComboBox(tableSetup.LoadSteps, False)
            table_widget.setCellWidget(selected_row, j, combo)
        elif key == "ViewType":
            combo = qtDesignerHooks.GetComboBox(tableSetup.viewTypeOptions, False)
            table_widget.setCellWidget(selected_row, j, combo)
        elif key == "GridSystem":
            combo = qtDesignerHooks.GetComboBox([list(grid.keys())[0] for grid in tableSetup.GridSystemNames], False)
            table_widget.setCellWidget(selected_row, j, combo)
        elif key == "ViewLabels":
            container = qtDesignerHooks.GetLabelAndButton("", selected_row, j, table_widget)
            table_widget.setCellWidget(selected_row, j, container)
        elif key == "GroupName":
            combo = qtDesignerHooks.GetComboBox(tableSetup.GroupNames, False)
            table_widget.setCellWidget(selected_row, j, combo)
        elif key == "DecimalPlaces":
            spinbox = qtDesignerHooks.GetSpinBox(0)
            table_widget.setCellWidget(selected_row, j, spinbox)
        elif key == "TextScale":
            spinbox = qtDesignerHooks.GetSpinBox(0)
            table_widget.setCellWidget(selected_row, j, spinbox)
        elif key == "MarkerScale":
            spinbox = qtDesignerHooks.GetSpinBox(0)
            table_widget.setCellWidget(selected_row, j, spinbox)
        elif key == "OutputPdf":
            checkbox = qtDesignerHooks.GetCheckbox(False)
            table_widget.setCellWidget(selected_row, j, checkbox)
        elif key == "OutputExcel":
            checkbox = qtDesignerHooks.GetCheckbox(False)
            table_widget.setCellWidget(selected_row, j, checkbox)

def copyRows(table_widget):
    """Copy all selected rows"""
    # Get rows where "Selected" is checked
    selected_rows = []
    for row in range(3, table_widget.rowCount()):  # Start from row 3 to skip headers
        selected_col = tableSetup.RequestKeys.index("Selected")
        checkbox = table_widget.cellWidget(row, selected_col)
        if checkbox and checkbox.isChecked():
            selected_rows.append(row)
    
    if not selected_rows:
        return
    
    # Copy all selected rows in their original order
    for row in selected_rows:
        # Create a copy of the request (adjust index for header rows)
        request_copy = statesAllRequests.Requests[row - 3].copy()
        statesAllRequests.Requests.append(request_copy)
        
        # Add a new row to the table
        new_row = table_widget.rowCount()
        table_widget.insertRow(new_row)
        
        # Map the copied request to the table
        for j, key in enumerate(tableSetup.RequestKeys):
            if key == "Selected":
                checkbox = qtDesignerHooks.GetCheckbox(request_copy.get(key, False))
                table_widget.setCellWidget(new_row, j, checkbox)
            elif key == "Run":
                combo = qtDesignerHooks.GetComboBox(tableSetup.runOptions, request_copy.get(key, False))
                table_widget.setCellWidget(new_row, j, combo)
            elif key == "DataType":
                combo = qtDesignerHooks.GetComboBox(list(tableSetup.dataOptions.keys()), request_copy.get(key, False))
                table_widget.setCellWidget(new_row, j, combo)
            elif key == "Data":
                combo = qtDesignerHooks.GetComboBox(tableSetup.dataOptions.get(request_copy.get("DataType", ""), []), request_copy.get(key, False))
                table_widget.setCellWidget(new_row, j, combo)
            elif key == "LoadCase":
                combo = qtDesignerHooks.GetComboBox(tableSetup.LoadCombinationNames, request_copy.get(key, False))
                table_widget.setCellWidget(new_row, j, combo)
            elif key == "LoadStep":
                combo = qtDesignerHooks.GetComboBox(tableSetup.LoadSteps, request_copy.get(key, False))
                table_widget.setCellWidget(new_row, j, combo)
            elif key == "ViewType":
                combo = qtDesignerHooks.GetComboBox(tableSetup.viewTypeOptions, request_copy.get(key, False))
                table_widget.setCellWidget(new_row, j, combo)
            elif key == "GridSystem":
                combo = qtDesignerHooks.GetComboBox([list(grid.keys())[0] for grid in tableSetup.GridSystemNames], request_copy.get(key, False))
                table_widget.setCellWidget(new_row, j, combo)
            elif key == "ViewLabels":
                container = qtDesignerHooks.GetLabelAndButton(', '.join(request_copy.get(key, [])), new_row, j, table_widget)
                table_widget.setCellWidget(new_row, j, container)
            elif key == "GroupName":
                combo = qtDesignerHooks.GetComboBox(tableSetup.GroupNames, request_copy.get(key, False))
                table_widget.setCellWidget(new_row, j, combo)
            elif key == "DecimalPlaces":
                spinbox = qtDesignerHooks.GetSpinBox(request_copy.get(key, 0))
                table_widget.setCellWidget(new_row, j, spinbox)
            elif key == "TextScale":
                spinbox = qtDesignerHooks.GetSpinBox(request_copy.get(key, 0))
                table_widget.setCellWidget(new_row, j, spinbox)
            elif key == "MarkerScale":
                spinbox = qtDesignerHooks.GetSpinBox(request_copy.get(key, 0))
                table_widget.setCellWidget(new_row, j, spinbox)
            elif key == "OutputPdf":
                checkbox = qtDesignerHooks.GetCheckbox(request_copy.get(key, False))
                table_widget.setCellWidget(new_row, j, checkbox)
            elif key == "OutputExcel":
                checkbox = qtDesignerHooks.GetCheckbox(request_copy.get(key, False))
                table_widget.setCellWidget(new_row, j, checkbox)

def runRequests(table_widget):
    """Run the selected requests"""
    # Initialize list to store selected requests
    selected_requests = []
    
    # Iterate through all rows (skipping header rows)
    for row in range(3, table_widget.rowCount()):
        # Check if row is selected
        selected_col = tableSetup.RequestKeys.index("Selected")
        checkbox = table_widget.cellWidget(row, selected_col)
        if not checkbox or not checkbox.isChecked():
            continue
            
        # Create a dictionary for this request
        request_data = {}
        
        # Get data from each column
        for j, key in enumerate(tableSetup.RequestKeys):
            widget = table_widget.cellWidget(row, j)
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
        
        # Add the request to our list
        selected_requests.append(request_data)
    
    # Return the list of selected requests
    return selected_requests


