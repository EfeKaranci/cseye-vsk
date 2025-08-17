import states.statesAllRequests as statesAllRequests
import hooks.basicHooks as BasicHooks


def CompositeBeamDesignFunction():
    BeamDesignResults = statesAllRequests.SelectedCSITables["Composite Beam Design Envelope - AISC 360-16"]
    FramesWithDesignResults=[x["UniqueName"] for x in BeamDesignResults]
    for index,Frame in enumerate(statesAllRequests.SelectedFramesForCurrentRequest):
        UniqueName=str(Frame["UniqueName"])
        if(statesAllRequests.RequestGroup=="" or UniqueName in statesAllRequests.RequestGroupFrames):
            FrameDesginResult=next((x for x in BeamDesignResults if x["UniqueName"] == UniqueName), None)
            if(FrameDesginResult!=None):
                DesignSect = FrameDesginResult["DesignSect"]
                bEffLeft = FrameDesginResult["bEffLeft"]
                bEffRight = FrameDesginResult["bEffRight"]
                StudLayout = FrameDesginResult["StudLayout"]
                OverallRatio = FrameDesginResult["OverallRatio"]
                ReacLeft = FrameDesginResult["ReacLeft"]
                ReacRt = FrameDesginResult["ReacRt"]
                MmaxPos = FrameDesginResult["MmaxPos"]
                StrPMCapacity = FrameDesginResult["StrPMCapacity"]
                StrPMMaxCapacity = FrameDesginResult["StrPMMaxCapacity"]
                PerComp = FrameDesginResult["PCC"]
                StrPMFullCapacity = FrameDesginResult["StrPMFullCapacity"]
                Mid,MidText,EndIText,EndJText=GetMidpointsandTextforPlotting(Frame,UniqueName,DesignSect,bEffLeft,bEffRight,StudLayout,OverallRatio,ReacLeft,ReacRt,StrPMCapacity,StrPMMaxCapacity,StrPMFullCapacity,PerComp,MmaxPos)
                Color = BasicHooks.GetStressColor(float(OverallRatio))
                statesAllRequests.SelectedFramesForCurrentRequest[index]["Color"]=Color
                statesAllRequests.OutputSheets[statesAllRequests.RequestNameFormat1].append(FrameDesginResult)
                statesAllRequests.PlotTable.append({"Pt2d":Mid,"Text":MidText})
                if(statesAllRequests.RequestData=="Design Reactions"):
                    PtI=Frame["Pt2dI"]
                    PtJ=Frame["Pt2dJ"]
                    Scale=0.65
                    PtIScaled = Mid + (PtI - Mid) * Scale
                    PtJScaled = Mid + (PtJ - Mid) * Scale
                    statesAllRequests.PlotTable.append({"Pt2d":PtIScaled,"Text":EndIText})
                    statesAllRequests.PlotTable.append({"Pt2d":PtJScaled,"Text":EndJText})

def GetMidpointsandTextforPlotting(Frame,UniqueName,DesignSect,bEffLeft,bEffRight,StudLayout,OverallRatio,ReacLeft,ReacRt,StrPMCapacity,StrPMMaxCapacity,StrPMFullCapacity,PerComp,MmaxPos):
    PtI=Frame["Pt2dI"]
    PtJ=Frame["Pt2dJ"]
    Mid = (PtI + PtJ) / 2
    MidText = "(" + UniqueName + ")"
    EndIText = ""
    EndJText = ""
    if(statesAllRequests.RequestData=="Stud Layout"):
        MidText+="\n"+str(DesignSect)+ "("+StudLayout+")"
    elif(statesAllRequests.RequestData=="Effective Width"):
        MidText+="\n"+"bEff = " +str(float(bEffLeft)+float(bEffRight))
    elif(statesAllRequests.RequestData=="Composite Capacities"):
        MidText+="\n"+"ΦMn"+"("+str(int(float(PerComp)))+"%)="+str(int(float(StrPMCapacity)))+"\n"+"ΦMn(100%)="+str(int(float(StrPMFullCapacity)))
    elif(statesAllRequests.RequestData=="Design Ratio"):
        MidText+="\n"+"DCR = "+str(round(float(OverallRatio),2))+"\n"+"Mu = "+ str(int(float(MmaxPos)))
    elif(statesAllRequests.RequestData=="Design Reactions"):
        EndIText=str(round(float(ReacLeft),1))
        EndJText=str(round(float(ReacRt),1))

    return Mid, MidText, EndIText, EndJText