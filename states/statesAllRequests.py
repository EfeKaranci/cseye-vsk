import database.tableSetup as tableSetup

sapModel=None
modelPath=None

StoryDefinitions=[]
TowerAndBaseDefinitions=[]
GridDefinitions=[]
GridSystems=[]
LoadCombinationDefinitions=[]
LoadCaseDefinitions=[]
GroupDefinitions=[]

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
LoadResultsRequested=""
#PRELIMINARY CSI DATA
ViewPlanesForAllRequests=[]
GridDefinitions=[]
GridSystems=[]
StoryDefinitions=[]
TowerAndBaseDefinitions=[]
PointObjectConnectivity=[]
FrameObjectConnectivity=[]
FloorObjectConnectivity=[]
LoadCombinationDefinitions=[]
AllElementForces=[]
SelectedPointsForAllRequests=[]
SelectedFramesForAllRequests=[]
SelectedFloorsForAllRequests=[]
SelectedPointNamesForAllRequests=[]
SelectedFrameNamesForAllRequests=[]
SelectedFloorNamesForAllRequests=[]
#CSI
SelectedCSITables={}
SapModel=None
ObjectsGroupName=""
EnvelopeComboKey={}
###OUTPUT
OutputSheets={}
figs=[]
###UNITS
ForceUnit=""
DisplacementUnit=""
MomentUnit=""
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
RequestDecimalPlaces=""
RequestTextScale=""
RequestCircleScale=""
###CALCULATED INDIVIDUAL REQUEST PARAMETERS
ViewPlaneForCurrentRequest={}
SelectedPointsForCurrentRequest=[]
SelectedFramesForCurrentRequest=[]
SelectedAreasForCurrentRequest=[]
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