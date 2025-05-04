from PyQt5.QtWidgets import QCheckBox, QComboBox, QSpinBox, QLabel, QPushButton, QWidget, QHBoxLayout
import database.tableSetup as tableSetup
import states.statesAllRequests as statesAllRequests

def GetCheckbox(value):
    checkbox = QCheckBox()
    checkbox.setChecked(bool(value))
    checkbox.setStyleSheet("margin-left: 6px;")
    return checkbox

def GetComboBox(values, value):
    combo = QComboBox()
    combo.addItems(values)
    if value:
        combo.setCurrentText(value)
    return combo

def GetSpinBox(value):
    spinbox = QSpinBox()
    spinbox.setValue(int(value))
    return spinbox

def GetLabelAndButton(value, row, col, table_widget):
    # Create a container widget
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    
    # Create and style the label
    label = QLabel(str(value))
    label.setStyleSheet("""
        QLabel {padding-left: 5px;border: none;}
    """)
    
    # Create and style the tooltip button
    tooltipButton = QPushButton("...")
    tooltipButton.setFixedSize(20, 20)
    tooltipButton.setStyleSheet("""
        QPushButton {
            background-color: #f0f0f0;border: 1px solid #d0d0d0;border-radius: 10px;font-weight: bold;}
        QPushButton:hover {background-color: #e0e0e0;}
    """)
    
    # Connect the button click to show the selection dialog
    def showDialog():
        # Get the current view type and grid system
        view_type_col = tableSetup.RequestKeys.index("ViewType")
        grid_system_col = tableSetup.RequestKeys.index("GridSystem")
        
        view_type = table_widget.cellWidget(row, view_type_col).currentText()
        grid_system = table_widget.cellWidget(row, grid_system_col).currentText()
        
        # Get current labels from the request data
        request = statesAllRequests.Requests[row - 3]  # Adjust for header rows
        current_labels = request.get("ViewLabels", [])
        
        # Create and show the dialog
        dialog = ViewSelectionDialog(view_type, grid_system, current_labels, table_widget)
        if dialog.exec_() == QDialog.Accepted:
            # Update the label with the new selection
            new_value = ', '.join(dialog.selected_labels)
            label.setText(new_value)
            
            # Update the request data
            request["ViewLabels"] = dialog.selected_labels
    
    tooltipButton.clicked.connect(showDialog)
    
    # Add widgets to layout
    layout.addWidget(label, 1)  # 1 means it will expand
    layout.addWidget(tooltipButton)
    return container 