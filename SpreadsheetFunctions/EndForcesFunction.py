import states.statesAllRequests as statesAllRequests
import hooks.AnalysisResultsHooks as AnalysisResultsHooks

def GetEndForcesSpreadsheet():
    #combine frame forces
    RequestedDataKey=RequestedDataDict[statesAllRequests.RequestData]["Key"]
    Looped=[]
    for Frame in statesAllRequests.SelectedFramesForCurrentRequest:
        UniqueName,Story,FrameType=str(Frame["UniqueName"]),Frame["Story"],Frame["FrameType"]
        print("0")
        if(UniqueName not in Looped):
            print("1")
            Looped.append(UniqueName)
            if(statesAllRequests.RequestGroup=="" or UniqueName in statesAllRequests.RequestGroupFrames):
                FrameResults = AnalysisResultsHooks.GetLoadResultsForObject(statesAllRequests.AllElementForces, UniqueName,"UniqueName")
                print("2")
                if(len(FrameResults)>0):
                    print("3")
                    Stations=[float(x["Station"]) for x in FrameResults]
                    FirstStation=min(Stations)
                    LastStation=max(Stations)
                    FirstStationResults=[x for x in FrameResults if float(x["Station"])==FirstStation]
                    LastStationResults=[x for x in FrameResults if float(x["Station"])==LastStation]
                    FirstStationGoverningResult=GetResultsForFrame(FirstStationResults,RequestedDataKey)
                    LastStationGoverningResult=GetResultsForFrame(LastStationResults,RequestedDataKey)
                    if(FirstStationGoverningResult!=None and LastStationGoverningResult!=None):
                        PtI=Frame["Pt2dI"]
                        PtJ = Frame["Pt2dJ"]
                        PtIScaled,PtJScaled=GetScaledEndPoints(PtI,PtJ)
                        EndIForce=float(FirstStationGoverningResult[RequestedDataKey])
                        EndJForce=float(LastStationGoverningResult[RequestedDataKey])
                        EndIOutputCase=FirstStationGoverningResult["OutputCase"]
                        EndJOutputCase=LastStationGoverningResult["OutputCase"]
                        MidText,MidPt=GetMidpointsandTextforPlotting(PtI,PtJ,UniqueName)
                        EndIText=GetEndpointsandTextforPlotting(EndIForce,EndIOutputCase)
                        EndJText=GetEndpointsandTextforPlotting(EndJForce,EndJOutputCase)
                        FirstStationGoverningResult["End"]="I"
                        LastStationGoverningResult["End"]="J"
                        statesAllRequests.OutputSheets[statesAllRequests.RequestNameFormat1].append(FirstStationGoverningResult)
                        statesAllRequests.OutputSheets[statesAllRequests.RequestNameFormat1].append(LastStationGoverningResult)
                        statesAllRequests.PlotTable.append({"Pt2d":PtIScaled,"Value":EndIForce,"Text":EndIText})
                        statesAllRequests.PlotTable.append({"Pt2d":PtJScaled,"Value":EndJForce,"Text":EndJText})
                        statesAllRequests.PlotTable.append({"Pt2d":MidPt,"Value":0,"Text":MidText})

RequestedDataDict={"P": {"Key":"P"},"V2":{"Key":"V2"},
                    "V3":{"Key":"V3"},"T":{"Key":"T"},
                    "M2":{"Key":"M2"},"M3":{"Key":"M3"}}

def GetResultsForFrame(FrameResults,RequestedDataKey):
    Forces = [x[RequestedDataKey] for x in FrameResults]
    Forces = [float(x) for x in Forces]
    if(statesAllRequests.RequestIsEnvelope=="No"):
        MaxForce = max(Forces, key=abs)
    elif(statesAllRequests.RequestIsEnvelope=="Yes"):
        if(statesAllRequests.RequestLoadStep=="max"):MaxForce = max(Forces)
        elif(statesAllRequests.RequestLoadStep=="min"):MaxForce = min(Forces)
        elif(statesAllRequests.RequestLoadStep=="abs max"):MaxForce = max(Forces, key=abs)
    FrameResult=next((x for x in FrameResults if float(x[RequestedDataKey]) == MaxForce), None)
    return FrameResult

def GetScaledEndPoints(PtI,PtJ):
    Scale=0.65
    MidPt = (PtI + PtJ) / 2.0
    # Calculate the new endpoints by scaling the displacement from the MidPt
    PtIScaled = MidPt + (PtI - MidPt) * Scale
    PtJScaled = MidPt + (PtJ - MidPt) * Scale
    return PtIScaled, PtJScaled

def GetMidpointsandTextforPlotting(PtI,PtJ,UniqueName):
    MidPt=(PtI+PtJ)/2
    Text = "(" + UniqueName + ")"
    return Text,MidPt

def GetEndpointsandTextforPlotting(EndForce,OutputCase):
    MaxForceRounded = round(EndForce, statesAllRequests.RequestDecimalPlaces)
    Text =str(MaxForceRounded)
    if (statesAllRequests.RequestIsEnvelope == "Yes"):
        Text = Text + "\n" + OutputCase
    return Text