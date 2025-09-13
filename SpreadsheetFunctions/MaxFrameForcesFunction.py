import states.statesAllRequests as statesAllRequests
import hooks.AnalysisResultsHooks as AnalysisResultsHooks

def GetMaxFrameForcesSpreadsheet():
    FrameSectionProperties=statesAllRequests.SelectedCSITables["Frame Assignments - Section Properties"]
    RequestedDataKey = RequestedDataDict[statesAllRequests.RequestData]["Key"]
    Looped=[]
    for Frame in statesAllRequests.SelectedFramesForCurrentRequest:
        UniqueName,Story=str(Frame["UniqueName"]),Frame["Story"]
        if(statesAllRequests.RequestGroup=="" or UniqueName in statesAllRequests.RequestGroupFrames):
            if(UniqueName not in Looped):
                FrameResults = AnalysisResultsHooks.GetLoadResultsForObject(statesAllRequests.AllElementForces, UniqueName, "UniqueName")
                if(len(FrameResults)>0):
                    FrameResult=GetResultsForFrame(FrameResults,RequestedDataKey)
                    if(FrameResult!=None):
                        SectProp = next((x for x in FrameSectionProperties if x["UniqueName"] == UniqueName), None)
                        SectProp=SectProp["SectProp"]
                        MaxForce=float(FrameResult[RequestedDataKey])
                        OutputCase=FrameResult["OutputCase"]
                        mid,Text=GetMidpointsandTextforPlotting(Frame,UniqueName,MaxForce,OutputCase,SectProp)
                        statesAllRequests.OutputSheets[statesAllRequests.RequestNameFormat1].append(FrameResult)
                        statesAllRequests.PlotTable.append({"Pt2d":mid,"Value":MaxForce,"Text":Text})
                        Looped.append(UniqueName)

RequestedDataDict={"P(Abs)": {"Key":"P"},
                   "P(Comp)":{"Key":"P"},
                    "P(Tens)":{"Key":"P"},
                   "V2(Abs)":{"Key":"V2"},
                    "V3(Abs)":{"Key":"V3"},
                   "T(Abs)":{"Key":"T"},
                   "M2(Abs)":{"Key":"M2"},
                   "M3(Abs)":{"Key":"M3"}
                   }

def GetResultsForFrame(FrameResults,RequestedDataKey):
    if (statesAllRequests.RequestData == "Max Frame Forces-P(Comp)"):
        Forces = [x[RequestedDataKey] for x in FrameResults]
        Forces = [float(x) for x in Forces]
        MaxForce = min(0, min(Forces))
    elif (statesAllRequests.RequestData == "Max Frame Forces-P(Tens)"):
        Forces = [x[RequestedDataKey] for x in FrameResults]
        Forces = [float(x) for x in Forces]
        MaxForce = max(0, max(Forces))
    else:
        Forces = [x[RequestedDataKey] for x in FrameResults]
        Forces = [float(x) for x in Forces]
        MaxForce = max(Forces, key=abs)
        if(statesAllRequests.RequestIsEnvelope=="Yes"):
            if(statesAllRequests.RequestLoadStep=="max"):
                MaxForce = max(Forces)
            if(statesAllRequests.RequestLoadStep=="min"):
                MaxForce = min(Forces)
            if(statesAllRequests.RequestLoadStep=="abs max"):
                MaxForce = max(Forces, key=abs)
    FrameResult=next((x for x in FrameResults if float(x[RequestedDataKey]) == MaxForce), None)
    return FrameResult

def GetMidpointsandTextforPlotting(Frame,UniqueName,MaxForce,OutputCase,SectProp):
    PtI, PtJ = Frame["Pt2dI"],Frame["Pt2dJ"]
    mid = (PtI + PtJ) / 2
    MaxForceRounded = round(MaxForce, statesAllRequests.RequestDecimalPlaces)
    Text = SectProp  + "\n"+str(MaxForceRounded)
    if (statesAllRequests.RequestIsEnvelope == "Yes"):
        Text = Text + "\n" + OutputCase
    return mid, Text