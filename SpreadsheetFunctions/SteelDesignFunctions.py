import states.statesAllRequests as statesAllRequests
import Hooks.BasicHooks as BasicHooks

def GetSteelDesign360_16():
    BeamDesignResults = statesAllRequests.SelectedCSITables["Steel Beam Envelope - AISC 360-16"]
    BraceDesignResults = statesAllRequests.SelectedCSITables["Steel Brace Envelope - AISC 360-16"]
    ColumnDesignResults = statesAllRequests.SelectedCSITables["Steel Column Envelope - AISC 360-16"]
    FramesWithDesignResults=[x["UniqueName"] for x in BeamDesignResults]+[x["UniqueName"] for x in BraceDesignResults]+[x["UniqueName"] for x in ColumnDesignResults]
    OriginalSheetName=statesAllRequests.RequestNameFormat1
    FirstDelimiterIndex=OriginalSheetName.find('_')
    NewBeamSheet=OriginalSheetName[:FirstDelimiterIndex] + "a" + OriginalSheetName[FirstDelimiterIndex:] +"_Beams"
    NewBraceSheet=OriginalSheetName[:FirstDelimiterIndex] + "b" + OriginalSheetName[FirstDelimiterIndex:] +"_Braces"
    NewColumnSheet=OriginalSheetName[:FirstDelimiterIndex] + "c" + OriginalSheetName[FirstDelimiterIndex:] +"_Columns"
    statesAllRequests.OutputSheets[NewBeamSheet] = []
    statesAllRequests.OutputSheets[NewBraceSheet] = []
    statesAllRequests.OutputSheets[NewColumnSheet] = []
    for index,Frame in enumerate(statesAllRequests.SelectedFramesForCurrentRequest):
        UniqueName=str(Frame["UniqueName"])
        if(statesAllRequests.RequestGroup=="" or UniqueName in FramesWithDesignResults):
            if(UniqueName in FramesWithDesignResults):
                FrameType=Frame["FrameType"]
                if(FrameType=="Beam"): FrameDesginResult=next((x for x in BeamDesignResults if x["UniqueName"] == UniqueName), None)
                if(FrameType=="Brace"): FrameDesginResult=next((x for x in BraceDesignResults if x["UniqueName"] == UniqueName), None)
                if(FrameType=="Column"): FrameDesginResult=next((x for x in ColumnDesignResults if x["UniqueName"] == UniqueName), None)
                if(FrameDesginResult!=None):
                    DesignSection=FrameDesginResult["DesignSect"]
                    PMMCombo=FrameDesginResult["PMMCombo"]
                    PMMSum=FrameDesginResult["PMMRatio"]
                    PMMRatio=PMMSum.split(" ")[0]
                    Mid,Text=GetMidpointsandTextforPlotting(Frame,UniqueName,DesignSection,PMMCombo,PMMSum,PMMRatio)
                    Color = BasicHooks.GetStressColor(float(PMMRatio))
                    statesAllRequests.SelectedFramesForCurrentRequest[index]["Color"]=Color
                    if(FrameType=="Beam"):
                        statesAllRequests.OutputSheets[NewBeamSheet].append(FrameDesginResult)
                    if(FrameType=="Brace"):
                        statesAllRequests.OutputSheets[NewBraceSheet].append(FrameDesginResult)
                    if(FrameType=="Column"):
                        statesAllRequests.OutputSheets[NewColumnSheet].append(FrameDesginResult)
                    statesAllRequests.PlotTable.append({"Pt2d":Mid,"Text":Text})

def GetMidpointsandTextforPlotting(Frame,UniqueName,DesignSection,PMMCombo,PMMSum,PMMRatio):
    PtI=Frame["Pt2dI"]
    PtJ=Frame["Pt2dJ"]
    Mid = (PtI + PtJ) / 2
    Text = "(" + UniqueName + ")"
    if(statesAllRequests.RequestData=="DCRs"):
        Text+="\n"+str(PMMRatio)+ "\n"+DesignSection
    elif(statesAllRequests.RequestData=="Design Combination"):
        Text+="\n"+PMMCombo
    elif(statesAllRequests.RequestData=="PMM Breakdown"):
        Text+="\n"+PMMSum
    return Mid, Text