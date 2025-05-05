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

