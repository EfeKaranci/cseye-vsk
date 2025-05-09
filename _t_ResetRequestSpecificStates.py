import states.statesAllRequests as statesAllRequests
import Hooks.BasicHooks as BasicHooks

def ResetRequestSpecificStates(Request,i):
    statesAllRequests.RequestViewType = Request['col5']
    statesAllRequests.RequestGridSystem = Request['col7']
    statesAllRequests.RequestViewLabel = Request['col6']
    statesAllRequests.RequestDataType = Request['col1']
    statesAllRequests.RequestData = Request['col2']
    statesAllRequests.RequestIsEnvelope = Request['IsEnvelope']
    statesAllRequests.RequestLoadCase = Request['col3']
    if(statesAllRequests.RequestIsEnvelope== "Yes"):
        statesAllRequests.RequestLoadCases = statesAllRequests.EnvelopeComboKey[statesAllRequests.RequestLoadCase]
    if(statesAllRequests.RequestIsEnvelope== "No"):
        statesAllRequests.RequestLoadCases = [statesAllRequests.RequestLoadCase]
    statesAllRequests.RequestLoadStep = Request['col4'].lower()
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
    statesAllRequests.RequestDecimalPlaces = int(Request['col9']) if BasicHooks.CheckForInteger(Request['col9']) else 1
    statesAllRequests.RequestTextScale = Request['col10'] if BasicHooks.CheckforPositivefloat(Request['col10']) else 1
    statesAllRequests.RequestCircleScale = float(Request['col11']) if BasicHooks.CheckforPositivefloat(Request['col11']) else 1
    ViewPlaneData =next((x for x in statesAllRequests.ViewPlanesForAllRequests
                         if x['ViewType'] == statesAllRequests.RequestViewType
                         and x['ViewLabels'] == statesAllRequests.RequestViewLabel
                         and x['GridSystem'] == statesAllRequests.RequestGridSystem), None)
    if (ViewPlaneData != None):
        statesAllRequests.ViewPlaneForCurrentRequest = ViewPlaneData['PlaneEquation']
    print("t")