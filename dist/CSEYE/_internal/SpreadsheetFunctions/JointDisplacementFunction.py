import states.statesAllRequests as statesAllRequests
import Hooks.AnalysisResultsHooks as AnalysisResultsHooks

import Hooks.BasicHooks as BasicHooks

def GetJointDisplacements():
    ModelDisplacements=statesAllRequests.SelectedCSITables["Joint Displacements"]
    RequestedDataKey = RequestedDataDict[statesAllRequests.RequestData]["Key"]
    for point in statesAllRequests.SelectedPointsForCurrentRequest:
        UniqueName,Story,pt2d=point["UniqueName"],point["Story"],point["Coords"]
        if(statesAllRequests.RequestGroup=="" or UniqueName in statesAllRequests.RequestGroupPoints):
            JointDisplacementResults=AnalysisResultsHooks.GetLoadResultsForObject(ModelDisplacements,UniqueName,"UniqueName")
            if (len(JointDisplacementResults) > 0):
                JointDisplacementResult = AnalysisResultsHooks.GetGoverningResultForObject(JointDisplacementResults, RequestedDataKey)
                if (JointDisplacementResult != None):
                    OutputCase = JointDisplacementResult["OutputCase"]
                    RequestedDispl = float(JointDisplacementResult[RequestedDataKey])
                    Text = GetMappedText(UniqueName, RequestedDispl, OutputCase)
                    statesAllRequests.OutputSheets[statesAllRequests.RequestNameFormat1].append(JointDisplacementResult)
                    statesAllRequests.PlotTable.append({"Pt2d":pt2d,"Value":RequestedDispl,"Text":Text})

RequestedDataDict={"Ux": {"Key":"Ux"},"Uy":{"Key":"Uy"},
                    "Uz":{"Key":"Uz"},"Rx":{"Key":"Rx"},
                    "Ry":{"Key":"Ry"},"Rz":{"Key":"Rz"}}

def GetMappedText(UniqueName,RequestedDispl,OutputCase):
    MappedDispl = round(RequestedDispl, statesAllRequests.RequestDecimalPlaces)
    MappedDispl = str(MappedDispl)
    Text = "(" + str(UniqueName) + ")" + "\n" + MappedDispl
    if (statesAllRequests.RequestIsEnvelope == "Yes"):
        Text = Text + "\n" + OutputCase
    return Text