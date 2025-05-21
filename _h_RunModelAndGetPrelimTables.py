import states.statesAllRequests as statesAllRequests
import Hooks.CSIHooks as CSIHooks
import database.tableSetup as tableSetup
import comtypes.automation
import _i_CheckforEnvelopes as _i_CheckforEnvelopes
import states.statesUI as statesUI
ProgramPath="C:\Program Files\Computers and Structures\ETABS 21\ETABS.exe"
def RunModelAndGetPrelimTables():
    statesUI.counter+=1
    statesUI.update_status()
    if(not all(x in tableSetup.DataThatDoNotRequireRunModel for x in statesAllRequests.DataTypesRequested)):
        CSIHooks.RunModel()
    if("Steel Design 360-16" in statesAllRequests.DataTypesRequested):
        ret=statesAllRequests.SapModel.DesignSteel.StartDesign()
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
    statesAllRequests.StoryDefinitions=CSIHooks.GetAndProcessCSITable('Story Definitions', "")
    statesAllRequests.TowerAndBaseDefinitions=CSIHooks.GetAndProcessCSITable('Tower and Base Story Definitions', "")
    statesAllRequests.GridDefinitions=CSIHooks.GetAndProcessCSITable("Grid Definitions - Grid Lines", "")
    statesAllRequests.GridSystems=CSIHooks.GetAndProcessCSITable("Grid Definitions - General", "")
    statesAllRequests.LoadCombinationDefinitions=CSIHooks.GetAndProcessCSITable('Load Combination Definitions', "")
    statesAllRequests.GroupAssignments=CSIHooks.GetAndProcessCSITable('Group Assignments', "")
    CSIHooks.GetAvailableCSITables()
    print("h")
    _i_CheckforEnvelopes.CheckForEnvelopes()

