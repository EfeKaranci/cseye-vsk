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

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class WelcomeScreen(QMainWindow):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.loadModelButton.clicked.connect(self.loadModel)
        
        # Set the window icon with absolute path
        icon_path = os.path.abspath("images/icon.png")
        print(f"Icon path: {icon_path}")
        print(f"Icon file exists: {os.path.exists(icon_path)}")
        icon = QIcon(icon_path)
        print(f"Icon is null: {icon.isNull()}")
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
    
    # Set the icon for the stacked widget with absolute path
    icon_path = os.path.abspath("images/icon.png")
    print(f"Stacked widget icon path: {icon_path}")
    print(f"Stacked widget icon file exists: {os.path.exists(icon_path)}")
    icon = QIcon(icon_path)
    print(f"Stacked widget icon is null: {icon.isNull()}")
    statesUI.widget.setWindowIcon(icon)
    
    statesUI.widget.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Existing")