import states.statesAllRequests as statesAllRequests
import hooks.basicHooks as BasicHooks


def CompositeBeamDesignFunction():
    BeamDesignResults = statesAllRequests.SelectedCSITables["Composite Beam Design Envelope - AISC 360-16"]
    BeamDesignResultsEnvelope = statesAllRequests.SelectedCSITables["Composite Beam Design Envelope"]
    StudLayouts = [float(x["StudLayout"]) for x in BeamDesignResults]
    bEffs = [float(x["bEffLeft"])+float(x["bEffRight"]) for x in BeamDesignResults]
    StrPMCapacities = [float(x["StrPMCapacity"]) for x in BeamDesignResults]
    Reactions = [float(x["ReacLeft"])+float(x["ReacRt"]) for x in BeamDesignResults]
    for index,Frame in enumerate(statesAllRequests.SelectedFramesForCurrentRequest):
        UniqueName=str(Frame["UniqueName"])
        if(statesAllRequests.RequestGroup=="" or UniqueName in statesAllRequests.RequestGroupFrames):
            FrameDesginResult=next((x for x in BeamDesignResults if x["UniqueName"] == UniqueName), None)
            if(FrameDesginResult!=None):
                if(UniqueName == "269"):
                    print(FrameDesginResult)
                DesignSect = FrameDesginResult["DesignSect"]
                bEffLeft = FrameDesginResult["bEffLeft"]
                bEffRight = FrameDesginResult["bEffRight"]
                bEff = float(bEffLeft)+float(bEffRight)
                StudLayout = FrameDesginResult["StudLayout"]
                OverallRatio = FrameDesginResult["OverallRatio"]
                ReacLeft = FrameDesginResult["ReacLeft"]
                ReacRt = FrameDesginResult["ReacRt"]
                Reac = float(ReacLeft)+float(ReacRt)
                MmaxPos = FrameDesginResult["MmaxPos"]
                StrPMCapacity = FrameDesginResult["StrPMCapacity"]
                StrPMMaxCapacity = FrameDesginResult["StrPMMaxCapacity"]
                PerComp = FrameDesginResult["PCC"]
                StrPMFullCapacity = FrameDesginResult["StrPMFullCapacity"]
                VibrationRatio = FrameDesginResult["EquipVelRat"]
                ShearRatio = FrameDesginResult["StrShrRat"]
                DefRatio, DeflectionRatioCombo = GetControllingDeflectionResult(FrameDesginResult)
                Mid,MidText,EndIText,EndJText=GetMidpointsandTextforPlotting(Frame,UniqueName,DesignSect,bEffLeft,bEffRight,StudLayout,OverallRatio,ReacLeft,ReacRt,StrPMCapacity,StrPMMaxCapacity,StrPMFullCapacity,PerComp,MmaxPos,VibrationRatio,ShearRatio,DefRatio,DeflectionRatioCombo)
                if(statesAllRequests.RequestData=="Stud Layout"):
                    Color = BasicHooks.GetStressColor(float(StudLayout)/max(StudLayouts))
                elif(statesAllRequests.RequestData=="Effective Width"):
                    Color = BasicHooks.GetStressColor(float(bEff)/max(bEffs))
                elif(statesAllRequests.RequestData=="Composite Capacities at Max DCR"):
                    Color = BasicHooks.GetStressColor(float(StrPMCapacity)/max(StrPMCapacities))
                elif(statesAllRequests.RequestData=="Design Ratio"):
                    Color = BasicHooks.GetStressColor(float(OverallRatio))
                elif(statesAllRequests.RequestData=="Design Reactions"):
                    Color = BasicHooks.GetStressColor(float(Reac)/max(Reactions))
                elif(statesAllRequests.RequestData=="Vibration Ratio"):
                    Color = BasicHooks.GetStressColor(float(VibrationRatio))
                elif(statesAllRequests.RequestData=="Shear Ratio"):
                    Color = BasicHooks.GetStressColor(float(ShearRatio))
                elif(statesAllRequests.RequestData=="Deflection Ratio"):
                    Color = BasicHooks.GetStressColor(float(DefRatio))
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

def GetMidpointsandTextforPlotting(Frame,UniqueName,DesignSect,bEffLeft,bEffRight,StudLayout,OverallRatio,ReacLeft,ReacRt,StrPMCapacity,StrPMMaxCapacity,StrPMFullCapacity,PerComp,MmaxPos,VibrationRatio,ShearRatio,DefRatio,DeflectionRatioCombo):
    PtI=Frame["Pt2dI"]
    PtJ=Frame["Pt2dJ"]
    Mid = (PtI + PtJ) / 2
    MidText = ""
    EndIText = ""
    EndJText = ""
    if(statesAllRequests.RequestData=="Stud Layout"):
        MidText+=str(DesignSect)+ "("+StudLayout+")"
    elif(statesAllRequests.RequestData=="Effective Width"):
        MidText+="bEff = " +str(float(bEffLeft)+float(bEffRight))
    elif(statesAllRequests.RequestData=="Composite Capacities at Max DCR"):
        MidText+="ΦMn"+"("+str(int(float(PerComp)))+"%)="+str(int(float(StrPMCapacity)))+"\n"+"ΦMn(100%)="+str(int(float(StrPMFullCapacity)))
    elif(statesAllRequests.RequestData=="Design Ratio"):
        MidText+=str(DesignSect)+ "("+StudLayout+")"+"\n"+"DCR = "+str(round(float(OverallRatio),2))
    elif(statesAllRequests.RequestData=="Design Reactions"):
        EndIText=str(round(float(ReacLeft),1))
        EndJText=str(round(float(ReacRt),1))
    elif(statesAllRequests.RequestData=="Vibration Ratio"):
        MidText+="Vib Ratio = "+str(round(float(VibrationRatio),2))
    elif(statesAllRequests.RequestData=="Shear Ratio"):
        MidText+="Shear Ratio = "+str(round(float(ShearRatio),2))
    elif(statesAllRequests.RequestData=="Deflection Ratio"):
        MidText+=DeflectionRatioCombo +" = "+str(round(float(DefRatio),2))
    return Mid, MidText, EndIText, EndJText

def GetControllingDeflectionResult(data):
    PostCompositeDeadLoadDeflectionRatio = data["PCDLDfRat"]
    SuperimposedDeadLoadDeflectionRatio = data["SDLDfRat"]
    LiveLoadDeflectionRatio = data["LLDfRat"]
    TotalCamberDeflectionRatio = data["TotCamDfRat"]
    DefRatio = max(float(PostCompositeDeadLoadDeflectionRatio), float(SuperimposedDeadLoadDeflectionRatio), float(LiveLoadDeflectionRatio), float(TotalCamberDeflectionRatio))
    if DefRatio == float(PostCompositeDeadLoadDeflectionRatio):
        DeflectionRatioCombo = "DL Ratio(Pre)"
    elif DefRatio == float(SuperimposedDeadLoadDeflectionRatio):
        DeflectionRatioCombo = "SDL+LL Ratio"
    elif DefRatio == float(LiveLoadDeflectionRatio):
        DeflectionRatioCombo = "LL Ratio"
    elif DefRatio == float(TotalCamberDeflectionRatio):
        DeflectionRatioCombo = "Total Ratio"
    return DefRatio, DeflectionRatioCombo