import states.statesAllRequests as statesAllRequests
import hooks.basicHooks as BasicHooks
import states.statesUI as statesUI
import database.tableSetup as tableSetup
def SetRequestStates(Request,i):
    RequestViewProperties(Request,i)
    RequestDataProperties(Request,i)
    RequestLoadCaseProperties(Request,i)
    RequestGroupProperties(Request,i)
    RequestNameProperties(Request,i)
    RequestFormatProperties(Request,i)
    print("s")

def RequestViewProperties(Request,i):
    statesAllRequests.RequestViewType = Request['ViewType']
    statesAllRequests.RequestGridSystem = Request['GridSystem']
    statesAllRequests.RequestViewLabel = Request['ViewLabels']
    ViewPlaneData =next((x for x in statesAllRequests.ViewPlanesForAllRequests
                        if x['ViewType'] == statesAllRequests.RequestViewType
                        and x['ViewLabels'] == statesAllRequests.RequestViewLabel
                        and x['GridSystem'] == statesAllRequests.RequestGridSystem), None)
    if (ViewPlaneData != None):
        statesAllRequests.ViewPlaneForCurrentRequest = ViewPlaneData['PlaneEquation']

def RequestDataProperties(Request,i):
    statesAllRequests.RequestDataType = Request['DataType']
    statesAllRequests.RequestData = Request['Data']

def RequestLoadCaseProperties(Request,i):
    statesAllRequests.RequestLoadStep = Request['LoadStep'].lower()
    statesAllRequests.RequestLoadCase = Request['LoadCase']
    statesAllRequests.RequestIsEnvelope = Request['IsEnvelope']
    if(statesAllRequests.RequestIsEnvelope== "Yes"):
        statesAllRequests.RequestLoadCases = statesAllRequests.EnvelopeComboKey[statesAllRequests.RequestLoadCase]
    if(statesAllRequests.RequestIsEnvelope== "No"):
        statesAllRequests.RequestLoadCases = [statesAllRequests.RequestLoadCase]

def RequestGroupProperties(Request,i):
    statesAllRequests.RequestGroup = Request['GroupName']
    if(statesAllRequests.RequestGroup!=""):
        statesAllRequests.RequestGroupPoints = [x["UniqueName"] for x in statesAllRequests.GroupAssignments if x["GroupName"] == statesAllRequests.RequestGroup and x["ObjectType"] == "Point"]
        statesAllRequests.RequestGroupFrames = [x["UniqueName"] for x in statesAllRequests.GroupAssignments if x["GroupName"] == statesAllRequests.RequestGroup and x["ObjectType"] == "Line"]
        statesAllRequests.RequestGroupAreas = [x["UniqueName"] for x in statesAllRequests.GroupAssignments if x["GroupName"] == statesAllRequests.RequestGroup and x["ObjectType"] == "Area"]

def RequestNameProperties(Request,i):
    if statesAllRequests.RequestDataType in tableSetup.DataWithNoLoads:
        statesAllRequests.RequestNameFormat1 = str(i + 1) + "_"+statesAllRequests.RequestGroup+ "_" + statesAllRequests.RequestViewLabel + "_" + statesAllRequests.RequestDataType + "_" + statesAllRequests.RequestData 
        statesAllRequests.RequestNameFormat2 = "Request: " + str(i + 1) + "\n" \
                                               +"View: " + statesAllRequests.RequestViewLabel + "\n" \
                                               +"Data: " + statesAllRequests.RequestDataType + "-" + statesAllRequests.RequestData + "\n" \
                                               +"Units: " + statesAllRequests.SelectedUnits + "\n" \
                                               +"Group: " + statesAllRequests.RequestGroup
    elif statesAllRequests.RequestDataType not in tableSetup.DataWithNoLoads:
        statesAllRequests.RequestNameFormat1 = str(i + 1) + "_" + statesAllRequests.RequestGroup+"_"+ statesAllRequests.RequestViewLabel + "_" + statesAllRequests.RequestDataType + "_" + statesAllRequests.RequestData + "_" + \
                                               statesAllRequests.RequestLoadCase + "_" + "Step-" + statesAllRequests.RequestLoadStep 
        statesAllRequests.RequestNameFormat2 = "Request: " + str(i + 1) + "\n" \
                                               +"View: " + statesAllRequests.RequestViewLabel + "\n" \
                                               +"Data: " + statesAllRequests.RequestDataType + "-" + statesAllRequests.RequestData + "\n" \
                                               +"Case: " + statesAllRequests.RequestLoadCase + "\n" \
                                               +"Step: " + statesAllRequests.RequestLoadStep + "\n" \
                                               +"Units: " + statesAllRequests.SelectedUnits + "\n" \
                                               +"Group: " + statesAllRequests.RequestGroup

def RequestFormatProperties(Request,i):
    statesAllRequests.RequestDecimalPlaces = int(Request['DecimalPlaces'])
    statesAllRequests.RequestTextScale = Request['TextScale'] if BasicHooks.CheckforPositivefloat(Request['TextScale']) else 1
    statesAllRequests.RequestCircleScale = float(Request['MarkerScale']) if BasicHooks.CheckforPositivefloat(Request['MarkerScale']) else 1

