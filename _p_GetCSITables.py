import states.statesAllRequests as statesAllRequests
import hooks.csiHooks as CSIHooks
import _q_RequestValidation as _q_RequestValidation
import states.statesUI as statesUI

def GetRequestedTables():
    statesUI.counter+=1
    statesUI.update_status()
    for key, value in statesAllRequests.SelectedCSITables.items():
        #for some requests its easier to just get all the data
        if(key in ["Element Joint Forces - Frame"]):
            TableData=CSIHooks.GetAndProcessCSITable(key,"")
        else:
            TableData=CSIHooks.GetAndProcessCSITable(key,"")
        statesAllRequests.SelectedCSITables[key]=TableData
    PostProcessCertainTables()
 
    CSIHooks.GetAvailableCSITables()
    print("p")
    _q_RequestValidation.RequestValidation()

def PostProcessCertainTables():
    if any(x in statesAllRequests.DataTypesRequested for x in ["End Forces", "Max Frame Forces"]):
        BeamForces = statesAllRequests.SelectedCSITables["Element Forces - Beams"];
        BraceForces = statesAllRequests.SelectedCSITables["Element Forces - Braces"];
        ColumnForces = statesAllRequests.SelectedCSITables["Element Forces - Columns"];
        for Beam in BeamForces:
            Beam.pop('Beam', None)
        for Brace in BraceForces:
            Brace.pop('Brace', None)
        for Column in ColumnForces:
            Column.pop('Column', None)
        statesAllRequests.AllElementForces= BeamForces + BraceForces + ColumnForces
