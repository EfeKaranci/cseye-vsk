import sys
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication,QMainWindow
from PyQt5.QtGui import QIcon
import comtypes.client
import _c_initializeModules as _c_initializeModules
import states.statesAllRequests as statesAllRequests
import _b_fetchModelData as _b_fetchModelData
import states.statesUI as statesUI
import Hooks.CSIHooks as CSIHooks
from qtDesigner.windowLoadModel import Ui_MainWindow

def get_icon_path():
    """Get the absolute path to the icon file"""
    # Get the absolute path of the current file
    current_file = os.path.abspath(__file__)
    print(f"Current file: {current_file}")
    
    # Get the directory containing the current file
    current_dir = os.path.dirname(current_file)
    print(f"Current directory: {current_dir}")
    
    # Construct the path to the icon
    icon_path = os.path.join(current_dir, "images", "icon.png")
    print(f"Attempting to load icon from: {icon_path}")
    
    # Check if file exists
    if os.path.exists(icon_path):
        print(f"Icon file exists at: {icon_path}")
    else:
        print(f"Icon file does not exist at: {icon_path}")
        # Try alternative path
        alt_path = os.path.join(os.path.dirname(current_dir), "images", "icon.png")
        print(f"Trying alternative path: {alt_path}")
        if os.path.exists(alt_path):
            print(f"Icon file exists at alternative path: {alt_path}")
            return alt_path
    
    return icon_path

class WelcomeScreen(QMainWindow):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.loadModelButton.clicked.connect(self.loadModel)
        
        # Set the window icon
        icon_path = get_icon_path()
        print(f"Loading icon from: {icon_path}")
        icon = QIcon(icon_path)
        if icon.isNull():
            print("Failed to load icon - icon is null")
        else:
            print("Successfully loaded icon")
        self.setWindowIcon(icon)

    def loadModel(self):
        CSIHooks.getModel()
        if (statesAllRequests.SapModel!=None):
            _b_fetchModelData.getModelData()
        else:
            self.ui.modelPath.setText("No model open")
            self.ui.modelPath.setStyleSheet("color: red;")

if __name__ == "__main__":
    app=QApplication(sys.argv)
    welcomeScreen=WelcomeScreen()
    statesUI.widget=QtWidgets.QStackedWidget()
    statesUI.widget.addWidget(welcomeScreen)
    statesUI.widget.resize(600, 600)
    
    # Set the icon for the stacked widget
    icon_path = get_icon_path()
    print(f"Loading stacked widget icon from: {icon_path}")
    icon = QIcon(icon_path)
    if icon.isNull():
        print("Failed to load stacked widget icon - icon is null")
    else:
        print("Successfully loaded stacked widget icon")
    statesUI.widget.setWindowIcon(icon)
    
    statesUI.widget.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Existing")