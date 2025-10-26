import states.statesAllRequests as statesAllRequests
import hooks.basicHooks as BasicHooks

def GetSteelDesign360_16():
    BeamDesignResults = statesAllRequests.SelectedCSITables["Steel Beam Envelope - AISC 360-16"]
    BraceDesignResults = statesAllRequests.SelectedCSITables["Steel Brace Envelope - AISC 360-16"]
    ColumnDesignResults = statesAllRequests.SelectedCSITables["Steel Column Envelope - AISC 360-16"]
    BeamDeflectionDesignResults = statesAllRequests.SelectedCSITables["Steel Beam Deflection Envelope - AISC 360-16"]
    CombinedResults = BeamDesignResults + BraceDesignResults + ColumnDesignResults
    FramesWithDesignResults=[x["UniqueName"] for x in CombinedResults]
    OriginalSheetName=statesAllRequests.RequestNameFormat1
    FirstDelimiterIndex=OriginalSheetName.find('_')
    NewBeamSheet=OriginalSheetName[:FirstDelimiterIndex] + "a" + OriginalSheetName[FirstDelimiterIndex:] +"_Beams"
    NewBraceSheet=OriginalSheetName[:FirstDelimiterIndex] + "b" + OriginalSheetName[FirstDelimiterIndex:] +"_Braces"
    NewColumnSheet=OriginalSheetName[:FirstDelimiterIndex] + "c" + OriginalSheetName[FirstDelimiterIndex:] +"_Columns"
    statesAllRequests.OutputSheets[NewBeamSheet] = []
    statesAllRequests.OutputSheets[NewBraceSheet] = []
    statesAllRequests.OutputSheets[NewColumnSheet] = []
    PMMCombos = [x["PMMCombo"] for x in CombinedResults]
    PMMComboColorMap = BasicHooks.MapLabelsToColors(PMMCombos)
    for index,Frame in enumerate(statesAllRequests.SelectedFramesForCurrentRequest):
        UniqueName=str(Frame["UniqueName"])
        if(statesAllRequests.RequestGroup=="" or UniqueName in statesAllRequests.RequestGroupFrames):
            if(UniqueName in FramesWithDesignResults):
                FrameType=Frame["FrameType"]
                FrameDesginResult=next((x for x in CombinedResults if x["UniqueName"] == UniqueName), None)
                if(FrameDesginResult!=None):
                    ThisBeamDeflectionResult = GetBeamDeflections(BeamDeflectionDesignResults, UniqueName)
                    DefRatio, DeflectionRatioCombo = GetControllingDeflectionResult(ThisBeamDeflectionResult)
                    DesignSection=FrameDesginResult["DesignSect"]
                    PMMCombo=FrameDesginResult["PMMCombo"]
                    PMMSum=FrameDesginResult["PMMRatio"]
                    PMMRatio=PMMSum.split(" ")[0]
                    PRatio=PMMSum.split(" ")[2]
                    M3Ratio=PMMSum.split(" ")[4]
                    M2Ratio=PMMSum.split(" ")[6]
                    V2Ratio=FrameDesginResult["VMajRatio"]
                    Mid,Text=GetMidpointsandTextforPlotting(Frame,UniqueName,DesignSection,PMMCombo,PMMSum,PMMRatio,PRatio,M3Ratio,M2Ratio,V2Ratio,DefRatio,DeflectionRatioCombo)
                    if(statesAllRequests.RequestData=="DCR"):
                        Color = BasicHooks.GetStressColor(float(PMMRatio))
                    elif(statesAllRequests.RequestData=="Design Combination"):
                        Color = PMMComboColorMap[PMMCombo]
                    elif(statesAllRequests.RequestData=="P Ratio"):
                        Color = BasicHooks.GetStressColor(float(PRatio))
                    elif(statesAllRequests.RequestData=="M2 Ratio"):
                        Color = BasicHooks.GetStressColor(float(M2Ratio))
                    elif(statesAllRequests.RequestData=="M3 Ratio"):
                        Color = BasicHooks.GetStressColor(float(M3Ratio))
                    elif(statesAllRequests.RequestData=="V2 Ratio"):
                        Color = BasicHooks.GetStressColor(float(V2Ratio))
                    elif(statesAllRequests.RequestData=="All Ratios"):
                        Color = BasicHooks.GetStressColor(float(PMMRatio))
                    elif(statesAllRequests.RequestData=="Deflection Ratio"):
                        Color = BasicHooks.GetStressColor(float(DefRatio))
                    statesAllRequests.SelectedFramesForCurrentRequest[index]["Color"]=Color
                    if(FrameType=="Beam"):
                        statesAllRequests.OutputSheets[NewBeamSheet].append(FrameDesginResult)
                    if(FrameType=="Brace"):
                        statesAllRequests.OutputSheets[NewBraceSheet].append(FrameDesginResult)
                    if(FrameType=="Column"):
                        statesAllRequests.OutputSheets[NewColumnSheet].append(FrameDesginResult)
                    statesAllRequests.PlotTable.append({"Pt2d":Mid,"Text":Text})
    if(statesAllRequests.RequestOutputExcel==False):
        del statesAllRequests.OutputSheets[NewBeamSheet]
        del statesAllRequests.OutputSheets[NewBraceSheet]
        del statesAllRequests.OutputSheets[NewColumnSheet]

def GetMidpointsandTextforPlotting(Frame,UniqueName,DesignSection,PMMCombo,PMMSum,PMMRatio,PRatio,M3Ratio,M2Ratio,V2Ratio,DefRatio,DeflectionRatioCombo):
    PtI=Frame["Pt2dI"]
    PtJ=Frame["Pt2dJ"]
    Mid = (PtI + PtJ) / 2
    Text = ""
    if(statesAllRequests.RequestData=="DCR"):
        Text+=DesignSection+"\n"+"DCR = "+str(PMMRatio)
    elif(statesAllRequests.RequestData=="Design Combination"):
        Text+=DesignSection+"\n"+str(PMMCombo)
    elif(statesAllRequests.RequestData=="P Ratio"):
        Text+=DesignSection+"\n"+"DCR(P) = "+str(PRatio)
    elif(statesAllRequests.RequestData=="M2 Ratio"):
        Text+=DesignSection+"\n"+"DCR(M2) = "+str(M2Ratio)
    elif(statesAllRequests.RequestData=="M3 Ratio"):
        Text+=DesignSection+"\n"+"DCR(M3) = "+str(M3Ratio)
    elif(statesAllRequests.RequestData=="All Ratios"):
        Text+=DesignSection+"\n"+"DCR(P) = "+str(PRatio)+"\n"+"DCR(M2) = "+str(M2Ratio)+"\n"+"DCR(M3) = "+str(M3Ratio)
    elif(statesAllRequests.RequestData=="V2 Ratio"):
        Text+=DesignSection+"\n"+"DCR(V2) = "+str(V2Ratio)
    elif(statesAllRequests.RequestData=="Deflection Ratio"):
        Text+=DesignSection+"\n"+DeflectionRatioCombo +" = "+str(DefRatio)
    return Mid, Text

def GetBeamDeflections(data, name, count=5):
    if not isinstance(data, list) or count <= 0:
        return []
    try:
        i = next(j for j, x in enumerate(data) if isinstance(x, dict) and x.get("UniqueName") == name)
    except StopIteration:
        return []
    return data[i : min(i + count, len(data))]

def GetControllingDeflectionResult(data):
    DefRatio = max(data, key=lambda x: float(x["DefRatio"]))
    DefRatio = float(DefRatio["DefRatio"])
    DeflectionRatioCombo = next((x['DeflType'] for x in data if float(x["DefRatio"]) == float(DefRatio)), None)
    return DefRatio, DeflectionRatioCombo
