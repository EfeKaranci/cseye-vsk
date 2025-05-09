import states.statesAllRequests as statesAllRequests
import Hooks.CSIHooks as CSIHooks
import _q_RequestValidation as _q_RequestValidation
def GetRequestedTables():
    for key, value in statesAllRequests.SelectedCSITables.items():
        #for some requests its easier to just get all the data
        if(key in ["Element Joint Forces - Frame"]):
            TableData=CSIHooks.GetAndProcessCSITable(key,"")
        else:
            TableData=CSIHooks.GetAndProcessCSITable(key,"")
        statesAllRequests.SelectedCSITables[key]=TableData
    PostProcessCertainTables()
    """ 
    for PointName in statesAllRequests.SelectedPointNamesForAllRequests:
            ret=statesAllRequests.SapModel.PointObj.SetGroupAssign(PointName, statesAllRequests.ObjectsGroupName,Remove=True)
    for FrameName in statesAllRequests.SelectedFrameNamesForAllRequests:
            ret=statesAllRequests.SapModel.FrameObj.SetGroupAssign(FrameName, statesAllRequests.ObjectsGroupName,Remove=True)
    for FloorName in statesAllRequests.SelectedFloorNamesForAllRequests:
            ret=statesAllRequests.SapModel.AreaObj.SetGroupAssign(FloorName, statesAllRequests.ObjectsGroupName,Remove=True)
    """
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
