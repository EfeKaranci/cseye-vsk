import database.csiTables as csiTables
import states.statesAllRequests as statesAllRequests
import _h_RunModelAndGetPrelimTables as _h_RunModelAndGetPrelimTables
import states.statesUI as statesUI
import hooks.csiHooks as CSIHooks

def GetCSITablesList():
    statesUI.counter+=1
    statesUI.update_status()
    for key, value in csiTables.AvailableTables.items():
        if (value['DataType'] == "All" or any(item in statesAllRequests.DataTypesRequested for item in value['DataType'])) \
                and (any(item in statesAllRequests.ViewTypesRequested for item in value['ViewTypes'])):
            statesAllRequests.SelectedCSITables[key] = ''
    print("g")
    _h_RunModelAndGetPrelimTables.RunModelAndGetPrelimTables()
