import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
import states.statesAllRequests as statesAllRequests
import database.tableSetup as tableSetup
import _e_WindowFeatures as _e_WindowFeatures
import _d_FileFeatures as _d_FileFeatures
from qtDesigner.windowSelectViews import Ui_Dialog as Ui_WindowSelectViews

class ViewSelectionDialog(QtWidgets.QDialog):
    def __init__(self, viewType, gridSystem, currentLabels, parent=None):
        super(ViewSelectionDialog, self).__init__(parent)
        self.ui = Ui_WindowSelectViews()
        self.ui.setupUi(self)
        # Set the label text based on view type
        self.ui.ViewsTypeLabel.setText("Select stories" if viewType == "Story" else "Select elevations")
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
        self.ui.verticalLayout2.addWidget(scrollArea)
        
        # Connect the save button
        self.ui.SaveViewButton.clicked.connect(self.save_selection)
        
        # Store the current labels for comparison
        self.currentLabels = currentLabels
        self.selected_labels = currentLabels.copy()  # Initialize with current labels
    
    def toggle_all_checkboxes(self, state):
        for checkbox in self.checkboxes:
            checkbox.setChecked(state == Qt.Checked)
    
    def save_selection(self):
        self.selected_labels = [checkbox.text() for checkbox in self.checkboxes if checkbox.isChecked()]
        self.accept()

def GetLabelAndButton(value, row, col, table_widget,request):
    # Create a container widget
    container = QtWidgets.QWidget()
    layout = QtWidgets.QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    
    # Create and style the label
    label = QtWidgets.QLabel(str(value))
    label.setStyleSheet("""
        QLabel {padding-left: 5px;border: none;}
    """)
    
    # Create and style the tooltip button
    tooltipButton = QtWidgets.QPushButton("...")
    tooltipButton.setFixedSize(20, 20)
    tooltipButton.setStyleSheet("""
        QPushButton {
            background-color: #f0f0f0;border: 1px solid #d0d0d0;border-radius: 10px;font-weight: bold;}
        QPushButton:hover {background-color: #e0e0e0;}
    """)
    
    # Connect the button click to show the selection dialog
    def showDialog(request):
        # Get the current view type and grid system
        view_type_col = tableSetup.RequestKeys.index("ViewType")
        grid_system_col = tableSetup.RequestKeys.index("GridSystem")
        
        view_type = table_widget.cellWidget(row, view_type_col).currentText()
        grid_system = table_widget.cellWidget(row, grid_system_col).currentText()
        
        # Get current labels from the request data
        current_labels = request.get("ViewLabels", [])
        if(len(current_labels) > 0):
            current_labels = current_labels[0].split(';')
            current_labels = [label.strip() for label in current_labels]
        
        # Create and show the dialog
        dialog = ViewSelectionDialog(view_type, grid_system, current_labels, table_widget)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            # Update the label with the new selection
            new_value = '; '.join(dialog.selected_labels)
            label.setText(new_value)
            
            # Update the request data
            request["ViewLabels"] = dialog.selected_labels
    
    tooltipButton.clicked.connect(lambda: showDialog(request))
    
    # Add widgets to layout
    layout.addWidget(label, 1)  # 1 means it will expand
    layout.addWidget(tooltipButton)
    return container 