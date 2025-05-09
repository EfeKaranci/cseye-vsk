import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication,QMainWindow
import comtypes.client
import _c_initializeModules as _c_initializeModules
import states.statesAllRequests as statesAllRequests
import _b_fetchModelData as _b_fetchModelData
import states.statesUI as statesUI
import Hooks.CSIHooks as CSIHooks
class WelcomeScreen(QMainWindow):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("qtDesigner/windowLoadModel.ui",self)
        self.loadModelButton.clicked.connect(self.loadModel)

    def loadModel(self):
        CSIHooks.getModel()
        if (statesAllRequests.SapModel!=None):
            _b_fetchModelData.getModelData()
        else:
            self.modelPath.setText("No model open")
            self.modelPath.setStyleSheet("color: red;")

if __name__ == "__main__":
    app=QApplication(sys.argv)
    welcomeScreen=WelcomeScreen()
    statesUI.widget=QtWidgets.QStackedWidget()
    statesUI.widget.addWidget(welcomeScreen)
    statesUI.widget.resize(600, 600)
    statesUI.widget.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Existing")