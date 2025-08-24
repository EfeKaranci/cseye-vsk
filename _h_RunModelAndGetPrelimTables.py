import states.statesAllRequests as statesAllRequests
import hooks.csiHooks as CSIHooks
import database.tableSetup as tableSetup
import comtypes.automation
import _i_CheckforEnvelopes as _i_CheckforEnvelopes
import states.statesUI as statesUI
ProgramPath=r"C:\Program Files\Computers and Structures\ETABS 21\ETABS.exe"
def RunModelAndGetPrelimTables():
    statesUI.counter+=1
    statesUI.update_status()
    if(not all(x in tableSetup.DataThatDoNotRequireRunModel for x in statesAllRequests.DataTypesRequested)):
        CSIHooks.RunModel()
    if("Steel Design 360-16" in statesAllRequests.DataTypesRequested):
        if(statesAllRequests.SapModel):
            ret=statesAllRequests.SapModel.DesignSteel.StartDesign()
    if("Composite Beam Design" in statesAllRequests.DataTypesRequested):
        if(statesAllRequests.SapModel):
            ret=statesAllRequests.SapModel.DesignCompositeBeam.StartDesign()
    #GetPreliminaryTables
    BeamConnectivity=CSIHooks.GetAndProcessCSITable('Beam Object Connectivity',"")
    for Beam in BeamConnectivity: Beam['FrameType']="Beam"
    BraceConnectivity=CSIHooks.GetAndProcessCSITable('Brace Object Connectivity',"")
    for Brace in BraceConnectivity: Brace['FrameType']="Brace"
    ColumnConnectivity=CSIHooks.GetAndProcessCSITable('Column Object Connectivity',"")
    for Column in ColumnConnectivity: Column['FrameType']="Column"
    statesAllRequests.FrameObjectConnectivity= BeamConnectivity + BraceConnectivity + ColumnConnectivity
    statesAllRequests.PointObjectConnectivity=CSIHooks.GetAndProcessCSITable('Point Object Connectivity', "")
    statesAllRequests.FloorObjectConnectivity=CSIHooks.GetAndProcessCSITable('Floor Object Connectivity', "")
    statesAllRequests.NullAreaObjectConnectivity=CSIHooks.GetAndProcessCSITable('Null Area Object Connectivity', "")
    statesAllRequests.AreaAssignments=CSIHooks.GetAndProcessCSITable("Area Assignments - Section Properties", "")
    statesAllRequests.StoryDefinitions=CSIHooks.GetAndProcessCSITable('Story Definitions', "")
    statesAllRequests.TowerAndBaseDefinitions=CSIHooks.GetAndProcessCSITable('Tower and Base Story Definitions', "")
    statesAllRequests.GridDefinitions=CSIHooks.GetAndProcessCSITable("Grid Definitions - Grid Lines", "")
    statesAllRequests.GridSystems=CSIHooks.GetAndProcessCSITable("Grid Definitions - General", "")
    statesAllRequests.LoadCombinationDefinitions=CSIHooks.GetAndProcessCSITable('Load Combination Definitions', "")
    statesAllRequests.GroupAssignments=CSIHooks.GetAndProcessCSITable('Group Assignments', "")
    print("h")
    _i_CheckforEnvelopes.CheckForEnvelopes()

