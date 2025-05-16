import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
import states.statesAllRequests as statesAllRequests
import database.tableSetup as tableSetup
import Hooks.qtDesignerHooks as qtDesignerHooks
import _f_ProcessRequests as _f_ProcessRequests
import Hooks.tableWidgetHooks as tableWidgetHooks
import states.statesUI as statesUI

def newRow(table_widget):
    """Add a new row to the table with default values"""
    # Get the current number of rows
    rowIndex = table_widget.rowCount()
    # Add a new row
    table_widget.insertRow(rowIndex)
    # Create a new request with default values
    new_request = statesAllRequests.defaultRow.copy()
    tableWidgetHooks.newRow(table_widget,rowIndex,new_request)
    # Map the new request to the table

def insertRowsBelow(table_widget):
    """Insert a new row below the selected row"""
    # Get the last row where "Selected" is checked
    rowIndex = None
    for row in range(3, table_widget.rowCount()):  # Start from row 3 to skip headers
        selected_col = tableSetup.RequestKeys.index("Selected")
        checkbox = table_widget.cellWidget(row, selected_col)
        if checkbox and checkbox.isChecked():
            rowIndex = row
    if rowIndex is None:
        return
    # Insert row in the table
    table_widget.insertRow(rowIndex + 1)
    # Create a new request with default values
    new_request = statesAllRequests.defaultRow.copy()
    # Insert at the correct position in Requests array (subtract 3 for header rows)
    tableWidgetHooks.newRow(table_widget,rowIndex + 1,new_request)

def insertRowsAbove(table_widget):
    """Insert a new row above the selected row"""
    # Get the first row where "Selected" is checked
    rowIndex = None
    for row in range(3, table_widget.rowCount()):  # Start from row 3 to skip headers
        selected_col = tableSetup.RequestKeys.index("Selected")
        checkbox = table_widget.cellWidget(row, selected_col)
        if checkbox and checkbox.isChecked():
            rowIndex = row
            break  # We only need the first selected row
    if rowIndex is None:
        return
    # Insert row in the table
    table_widget.insertRow(rowIndex)
    # Create a new request with default values
    new_request = statesAllRequests.defaultRow.copy()
    # Insert at the correct position in Requests array (subtract 3 for header rows)
    # Map the new request to the table
    tableWidgetHooks.newRow(table_widget,rowIndex,new_request)

def copyRows(table_widget):
    """Copy all selected rows"""
    # Get rows where "Selected" is checked
    selectedRows,selected_Indices = tableWidgetHooks.getTableRequests(table_widget,"Selected","True")
    if not selectedRows:
        return
    # Copy all selected rows in their original order
    for index,row in enumerate(selectedRows):
        NewRowIndex = selected_Indices[index]+1
        table_widget.insertRow(NewRowIndex)
        tableWidgetHooks.newRow(table_widget,NewRowIndex,row)
        selected_Indices=[x+1 for x in selected_Indices]
        # Map the copied request to the table


def deleteRows(table_widget):
    """Delete selected rows from the table"""
    # Get rows where "Selected" is checked
    selectedRows = []
    for row in range(3, table_widget.rowCount()):  # Start from row 3 to skip headers
        selected_col = tableSetup.RequestKeys.index("Selected")
        checkbox = table_widget.cellWidget(row, selected_col)
        if checkbox and checkbox.isChecked():
            selectedRows.append(row)
    # Sort rows in descending order to avoid index shifting
    for row in sorted(selectedRows, reverse=True):
        table_widget.removeRow(row)
        # Adjust the index for the Requests array (subtract 3 for header rows)

def runRequests(table_widget,outputFilePath,outputFolderPath,units,posViewTolerance,negViewTolerance):
    """Run the selected requests"""
    # Initialize list to store selected requests
    selected_requests,selected_Indices = tableWidgetHooks.getTableRequests(table_widget,"Run","Run")
    
    # Create and show the status message box
    status_box = QtWidgets.QMessageBox()
    status_box.setWindowTitle("Processing Status")
    status_box.setStandardButtons(QtWidgets.QMessageBox.NoButton)  # Remove buttons
    status_box.show()
    
    # Set the status box in statesUI
    statesUI.status_box = status_box
    
    try:
        # Reset counter before starting
        statesUI.counter = 0
        
        # Process the requests
        _f_ProcessRequests.processRequests(selected_requests,outputFilePath,outputFolderPath,units,posViewTolerance,negViewTolerance)
        
        # Show completion message
        status_box.setText("Requests completed successfully!")
        status_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        status_box.exec_()
        
    except Exception as e:
        # Show error message
        status_box.setText(f"Error encountered: {str(e)}")
        status_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        status_box.exec_()
    finally:
        # Clear the status box reference
        statesUI.status_box = None


