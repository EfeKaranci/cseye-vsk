import states.statesAllRequests as statesAllRequests
import hooks.basicHooks as basicHooks

def GetAndProcessCSITable(tableName,groupName):
    table = statesAllRequests.sapModel.DatabaseTables.GetTableForDisplayArray(tableName, "", groupName, 21, "")
    NoOfColumns = len(table[2])
    table = table[2] + table[4]
    table = [table[i:i + NoOfColumns] for i in range(0, len(table), NoOfColumns)]
    table = basicHooks.ConvertListOfListsToListOfDictionaries((table))
    return table