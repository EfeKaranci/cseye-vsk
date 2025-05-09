import states.statesAllRequests as statesAllRequests
import Hooks.AnalysisResultsHooks as AnalysisResultsHooks

def GetJointDrifts():
    ModelDrifts=statesAllRequests.SelectedCSITables["Joint Drifts"]
    RequestedDataKey=RequestedDataDict[statesAllRequests.RequestData]["Key"]
    JointsWithDriftResults=[x["UniqueName"] for x in ModelDrifts]
    for point in statesAllRequests.SelectedPointsForCurrentRequest:
        UniqueName,pt2d=point["UniqueName"],point["Coords"]
        if(UniqueName in JointsWithDriftResults):
            JointDriftResults=AnalysisResultsHooks.GetLoadResultsForObject(ModelDrifts,UniqueName,"UniqueName")
            if(len(JointDriftResults)>0):
                JointDriftResult=AnalysisResultsHooks.GetGoverningResultForObject(JointDriftResults,RequestedDataKey)
                if(JointDriftResult!=None):
                    OutputCase=JointDriftResult["OutputCase"]
                    RequestedDrift=float(JointDriftResult[RequestedDataKey])
                    Text=GetMappedText(UniqueName,RequestedDrift,OutputCase)
                    statesAllRequests.OutputSheets[statesAllRequests.RequestNameFormat1].append(JointDriftResult)
                    statesAllRequests.PlotTable.append({"Pt2d":pt2d,"Value":RequestedDrift,"Text":Text})
                    
RequestedDataDict={"X": {"Key":"DriftX"},"Y":{"Key":"DriftY"},}

def GetMappedText(UniqueName,RequestedDrift,OutputCase):
    MappedDrift = round(RequestedDrift, statesAllRequests.RequestDecimalPlaces)
    Text = "(" + str(UniqueName) + ")" + "\n" + str(MappedDrift)
    if (statesAllRequests.RequestIsEnvelope == "Yes"):
        Text = Text + "\n" + OutputCase
    return Text