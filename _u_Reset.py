import states.statesAllRequests as statesAllRequests
def ResetRequestSpecificStates():
    ###SPECIFIED INDIVIDUAL REQUEST PARAMETER
    statesAllRequests.RequestGridSystem = ""
    statesAllRequests.RequestViewType = ""
    statesAllRequests.RequestViewLabel = ""
    statesAllRequests.RequestIsEnvelope = ""
    statesAllRequests.RequestLoadCase = ""
    statesAllRequests.RequestLoadCases = []
    statesAllRequests.RequestLoadStep = ""
    statesAllRequests.RequestNameFormat1 = ""
    statesAllRequests.RequestNameFormat2 = ""
    statesAllRequests.RequestData = ""
    statesAllRequests.RequestDataType = ""
    statesAllRequests.RequestDecimalPlaces = ""
    statesAllRequests.RequestTextScale = ""
    statesAllRequests.RequestCircleScale = ""
    ###CALCULATED INDIVIDUAL REQUEST PARAMETERS
    statesAllRequests.ViewPlaneForCurrentRequest = {}
    statesAllRequests.SelectedPointsForCurrentRequest = []
    statesAllRequests.SelectedFramesForCurrentRequest = []
    statesAllRequests.SelectedAreasForCurrentRequest = []
    statesAllRequests.SelectedPointNamesForCurrentRequest=[]
    statesAllRequests.SelectedFrameNamesForCurrentRequest=[]
    statesAllRequests.SelectedAreaNamesForCurrentRequest=[]
    statesAllRequests.PlanColumns = []
    statesAllRequests.PlanBraces = []
    statesAllRequests.PlotTable = []
    statesAllRequests.ax = ""
    ###PLOTSETTINGS
    statesAllRequests.origin = ""
def ResetGeneralStates():
    statesAllRequests.Requests = []
    statesAllRequests.OutputName = ""
    statesAllRequests.ModelPath = ""
    statesAllRequests.OutputFolder = ""
    # TYPES REQUESTED
    statesAllRequests.DataTypesRequested = ""
    statesAllRequests.ViewTypesRequested = ""
    statesAllRequests.ViewLabelsRequested = ""
    statesAllRequests.LoadResultsRequested = ""
    #ALL GEOMETRY REQUESTED
    statesAllRequests.ViewPlanesForAllRequests = []
    statesAllRequests.GridDefinitions=[]
    statesAllRequests.GridSystems=[]
    statesAllRequests.StoryDefinitions=[]
    statesAllRequests.TowerAndBaseDefinitions=[]
    statesAllRequests.PointObjectConnectivity=[]
    statesAllRequests.FrameObjectConnectivity=[]
    statesAllRequests.FloorObjectConnectivity=[]
    statesAllRequests.LoadCombinationDefinitions=[]
    statesAllRequests.AllElementForces = []
    statesAllRequests.SelectedPointsForAllRequests=[]
    statesAllRequests.SelectedFramesForAllRequests=[]
    statesAllRequests.SelectedFloorsForAllRequests=[]
    statesAllRequests.SelectedPointNamesForAllRequests=[]
    statesAllRequests.SelectedFrameNamesForAllRequests=[]
    statesAllRequests.SelectedFloorNamesForAllRequests=[]
    # CSI
    statesAllRequests.SelectedCSITables = {}
    statesAllRequests.SapModel = None
    statesAllRequests.ObjectsGroupName= ""
    statesAllRequests.EnvelopeComboKey={}
    ###OUTPUT
    statesAllRequests.OutputSheets = {}
    statesAllRequests.figs = []
    statesAllRequests.figsNames = []
    ###UNITS
    statesAllRequests.ForceUnit = ""
    statesAllRequests.DisplacementUnit = ""
    statesAllRequests.MomentUnit = ""
    print("u")