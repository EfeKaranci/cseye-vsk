import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication,QMainWindow
import comtypes.client
import _2_initializeModules as _2_initializeModules
import states.statesAllRequests as statesAllRequests
import _1_fetchModelData as _1_fetchModelData
import states.statesUI as statesUI
class WelcomeScreen(QMainWindow):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("qtDesigner/windowLoadModel.ui",self)
        self.loadModelButton.clicked.connect(self.loadModel)

    def loadModel(self):
        getModel()
        if (statesAllRequests.sapModel!=None):
            _1_fetchModelData.getModelData()
        else:
            self.modelPath.setText("No model open")
            self.modelPath.setStyleSheet("color: red;")

def getModel():
    helper = comtypes.client.CreateObject("ETABSv1.Helper")
    helper = helper.QueryInterface(comtypes.gen.ETABSv1.cHelper)
    myETABSObject = helper.GetObject("CSI.ETABS.API.ETABSObject")
    if(myETABSObject!=None):
        statesAllRequests.sapModel = myETABSObject.SapModel
        statesAllRequests.modelPath = statesAllRequests.sapModel.GetModelFilename()
    else:
        return None

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