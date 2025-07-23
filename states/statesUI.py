from typing import Optional
from PyQt5.QtWidgets import QStackedWidget, QTableWidget, QLabel

widget: Optional[QStackedWidget] = None
tableWidget: Optional[QTableWidget] = None
counter: int = 0
status_box: Optional[QLabel] = None
counterMessages={
    1:"Processing Requests",
    2:"Getting Required CSITables",
    3:"Running Model",
    4:"Checking for Envelopes",
    5:"Setting Model Units",
    6:"Modifying Requests",
    7:"Getting Planes",
    8:"Getting All Selected Points",
    9:"Getting All Selected Frames and Floors",
    10:"Assigning Selected Objects to Group",
    11:"Getting CSITables",
    12:"Validating Requests",
    13:"Mapping Loop",
    14:"Writing Files"
    }

def update_status():
    """Update the status message box with the current processing stage"""
    global status_box, counter
    if status_box is not None and counter in counterMessages:
        status_box.setText(counterMessages[counter])
        # Force the message box to update
        status_box.repaint()
