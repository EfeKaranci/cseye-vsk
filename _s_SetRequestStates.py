import states.statesAllRequests as statesAllRequests
import Hooks.BasicHooks as BasicHooks

def SetRequestStates(Request,i):
    statesAllRequests.RequestViewType = Request['ViewType']
    statesAllRequests.RequestGridSystem = Request['GridSystem']
    statesAllRequests.RequestViewLabel = Request['ViewLabels']
    statesAllRequests.RequestDataType = Request['DataType']
    statesAllRequests.RequestData = Request['Data']
    statesAllRequests.RequestIsEnvelope = Request['IsEnvelope']
    statesAllRequests.RequestLoadCase = Request['LoadCase']
    if(statesAllRequests.RequestIsEnvelope== "Yes"):
        statesAllRequests.RequestLoadCases = statesAllRequests.EnvelopeComboKey[statesAllRequests.RequestLoadCase]
    if(statesAllRequests.RequestIsEnvelope== "No"):
        statesAllRequests.RequestLoadCases = [statesAllRequests.RequestLoadCase]
    statesAllRequests.RequestLoadStep = Request['LoadStep'].lower()
    statesAllRequests.RequestNameFormat1 = str(i + 1) + "_" + statesAllRequests.RequestViewLabel + "_" + statesAllRequests.RequestDataType + "_" + statesAllRequests.RequestData + "_" + \
                                           statesAllRequests.RequestLoadCase + "_" + "Step-" + statesAllRequests.RequestLoadStep

    RequestFormatType1DataTypes=["Framing Plans","Steel Design 360-16","Frame Releases","Frame Modifiers","Restraints","Tributary Areas"]
    if statesAllRequests.RequestDataType in RequestFormatType1DataTypes:
        statesAllRequests.RequestNameFormat1 = str(i + 1) + "_" + statesAllRequests.RequestViewLabel + "_" + statesAllRequests.RequestDataType + "_" + statesAllRequests.RequestData
        statesAllRequests.RequestNameFormat2 = "Request: " + str(i + 1) + "\n" \
                                               +"View: " + statesAllRequests.RequestViewLabel + "\n" \
                                               +"Data: " + statesAllRequests.RequestDataType + "-" + statesAllRequests.RequestData + "\n" \
                                               +"Units: " + statesAllRequests.SelectedUnits
    if statesAllRequests.RequestDataType not in RequestFormatType1DataTypes:
        statesAllRequests.RequestNameFormat1 = str(i + 1) + "_" + statesAllRequests.RequestViewLabel + "_" + statesAllRequests.RequestDataType + "_" + statesAllRequests.RequestData + "_" + \
                                               statesAllRequests.RequestLoadCase + "_" + "Step-" + statesAllRequests.RequestLoadStep
        statesAllRequests.RequestNameFormat2 = "Request: " + str(i + 1) + "\n" \
                                               +"View: " + statesAllRequests.RequestViewLabel + "\n" \
                                               +"Data: " + statesAllRequests.RequestDataType + "-" + statesAllRequests.RequestData + "\n" \
                                               +"Case: " + statesAllRequests.RequestLoadCase + "\n" \
                                               +"Step: " + statesAllRequests.RequestLoadStep + "\n" \
                                               +"Units: " + statesAllRequests.SelectedUnits
    statesAllRequests.RequestDecimalPlaces = int(Request['DecimalPlaces']) if BasicHooks.CheckForInteger(Request['DecimalPlaces']) else 1
    statesAllRequests.RequestTextScale = Request['TextScale'] if BasicHooks.CheckforPositivefloat(Request['TextScale']) else 1
    statesAllRequests.RequestCircleScale = float(Request['MarkerScale']) if BasicHooks.CheckforPositivefloat(Request['MarkerScale']) else 1
    ViewPlaneData =next((x for x in statesAllRequests.ViewPlanesForAllRequests
                         if x['ViewType'] == statesAllRequests.RequestViewType
                         and x['ViewLabels'] == statesAllRequests.RequestViewLabel
                         and x['GridSystem'] == statesAllRequests.RequestGridSystem), None)
    if (ViewPlaneData != None):
        statesAllRequests.ViewPlaneForCurrentRequest = ViewPlaneData['PlaneEquation']
    print("s")