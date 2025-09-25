import database.tableSetup as tableSetup

sapModel=None
modelPath=None

StoryDefinitions=[]
TowerAndBaseDefinitions=[]
GridDefinitions=[]
GridSystems=[]
LoadCombinationDefinitions=[]
LoadCaseDefinitions=[]
GroupAssignments=[]

defaultRow={tableSetup.RequestKeys[0]:False,
            tableSetup.RequestKeys[1]:"Run",
            tableSetup.RequestKeys[2]:"Framing", tableSetup.RequestKeys[3]:"Sections",
            tableSetup.RequestKeys[4]:"", tableSetup.RequestKeys[5]:"",
            tableSetup.RequestKeys[6]:"", tableSetup.RequestKeys[7]:"",tableSetup.RequestKeys[8]:[""], 
            tableSetup.RequestKeys[9]:"",
            tableSetup.RequestKeys[10]:1, tableSetup.RequestKeys[11]:1, tableSetup.RequestKeys[12]:1,
            tableSetup.RequestKeys[13]:True,tableSetup.RequestKeys[14]:True}

###GENERAL REQUEST PARAMETERS
Requests = []
OutputName = ""
ModelPath = ""
OutputFolder = ""
SelectedUnits = ""
PosViewTolerance = ""
NegViewTolerance = ""
#TYPES REQUESTED
DataTypesRequested =""
ViewTypesRequested=""
ViewLabelsRequested=""
LoadResultsRequested=[]
#PRELIMINARY CSI DATA
ViewPlanesForAllRequests=[]
PointObjectConnectivity=[]
FrameObjectConnectivity=[]
FloorObjectConnectivity=[]
NullAreaObjectConnectivity=[]
AreaAssignments=[]
AreaAssignments=[]
AllElementForces=[]
SelectedPointsForAllRequests=[]
SelectedFramesForAllRequests=[]
SelectedFloorsForAllRequests=[]
SelectedNullAreasForAllRequests=[]
SelectedPointNamesForAllRequests=[]
SelectedFrameNamesForAllRequests=[]
SelectedFloorNamesForAllRequests=[]
SelectedNullAreaNamesForAllRequests=[]
#CSI
SelectedCSITables={}
SapModel=None
EnvelopeComboKey={}
###OUTPUT
OutputSheets={}
figs=[]
figsNames=[]
###UNITS
DisplacementUnit=""
###SPECIFIED INDIVIDUAL REQUEST PARAMETER
RequestGridSystem=""
RequestViewType=""
RequestViewLabel=""
RequestIsEnvelope=""
RequestLoadCase=""#actual name of load requested
RequestLoadCases=[]#for envelope load case senarios
RequestLoadStep=""
RequestNameFormat1=""
RequestNameFormat2=""
RequestData=""
RequestDataType=""
RequestGroup=""
RequestGroupPoints=[]
RequestGroupFrames=[]
RequestGroupAreas=[]
RequestDecimalPlaces=[]
RequestTextScale=""
RequestCircleScale=""
RequestOutputPdf=""
RequestOutputExcel=""
###CALCULATED INDIVIDUAL REQUEST PARAMETERS
ViewPlaneForCurrentRequest={}
SelectedPointsForCurrentRequest=[]
SelectedFramesForCurrentRequest=[]
SelectedAreasForCurrentRequest=[]
SelectedNullAreasForCurrentRequest=[]
SelectedPointNamesForCurrentRequest=[]
SelectedFrameNamesForCurrentRequest=[]
SelectedAreaNamesForCurrentRequest=[]
PlanColumns=[]
PlanBraces=[]
PlotTable=[]
ax=""
###MAPS
###PLOTSETTINGS
origin=""