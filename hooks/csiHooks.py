import states.statesAllRequests as statesAllRequests
import Hooks.BasicHooks as BasicHooks
import comtypes.client
def GetAndProcessCSITable(tableName,groupName):
    table = statesAllRequests.SapModel.DatabaseTables.GetTableForDisplayArray(tableName, "", groupName, 21, "")
    NoOfColumns = len(table[2])
    table = table[2] + table[4]
    table = [table[i:i + NoOfColumns] for i in range(0, len(table), NoOfColumns)]
    table = BasicHooks.ConvertListOfListsToListOfDictionaries((table))
    return table

def RunModel():
    ret = statesAllRequests.SapModel.Analyze.RunAnalysis()
    return ret

def getModel():
    helper = comtypes.client.CreateObject("ETABSv1.Helper")
    helper = helper.QueryInterface(comtypes.gen.ETABSv1.cHelper)
    myETABSObject = helper.GetObject("CSI.ETABS.API.ETABSObject")
    if(myETABSObject!=None):
        statesAllRequests.SapModel = myETABSObject.SapModel
        statesAllRequests.modelPath = statesAllRequests.SapModel.GetModelFilename()
    else:
        return None

def GetAvailableCSITables():
    Tables=statesAllRequests.SapModel.DatabaseTables.GetAvailableTables();
    return Tables[1]