import states.statesAllRequests as statesAllRequests
import hooks.basicHooks as BasicHooks
import comtypes.client
import re
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
    BasicHooks.WriteTable(Tables,"test.xlsx")
    return Tables[1]

def SortAlphanumeric(lst):
    """
    Sorts a list of alphanumeric strings in natural (human-friendly) order.
    
    Example:
        >>> SortAlphanumeric(["item2", "item10", "item1", "apple", "123", "20birds"])
        ['123', '20birds', 'apple', 'item1', 'item2', 'item10']
    """
    def alphanum_key(s):
        # Split into runs of digits and non-digits, convert digit runs to ints
        return [
            int(chunk) if chunk.isdigit() else chunk.lower()
            for chunk in re.split(r'(\d+)', s)
        ]
    
    return sorted(lst, key=alphanum_key)

