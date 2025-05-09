import states.statesAllRequests as statesAllRequests

def GetModifiers():
    ModelModifiers=statesAllRequests.SelectedCSITables["Frame Assignments - Property Modifiers"]
    RequestedDataKey=RequestedDataDict[statesAllRequests.RequestData]["Key"]
    for index, Frame in enumerate(statesAllRequests.SelectedFramesForCurrentRequest):
        UniqueName, Story = Frame["UniqueName"], Frame["Story"]
        ModifierResult=next((x for x in ModelModifiers if x["UniqueName"] == UniqueName), None)
        if (ModifierResult != None):
            Modifier=ModifierResult[RequestedDataKey]
            if (float(Modifier)!=1.0):
                statesAllRequests.SelectedFramesForCurrentRequest[index]["Color"]="red"
                #Get release text
                Text=GetModifierText(Modifier)
                #Get MidPoint
                MidPt=GetMidPoints(Frame)
                statesAllRequests.OutputSheets[statesAllRequests.RequestNameFormat1].append(ModifierResult)
                statesAllRequests.PlotTable.append({"Pt2d":MidPt,"Text":Text})

RequestedDataDict={"Area": {"Key":"AMod"},"As2":{"Key":"A2Mod"},"As3":{"Key":"A3Mod"},
                   "J":{"Key":"JMod"},"I2":{"Key":"I2Mod"},"I3":{"Key":"I3Mod"},
                   "Mass":{"Key":"MMod"},"Weight":{"Key":"WMod"}}

def GetMidPoints(Frame):
    PtI = Frame[6]
    PtJ = Frame[7]
    MidPt=(PtI+PtJ)/2
    return MidPt

def GetModifierText(Modifier):
    Text=RequestedDataDict[statesAllRequests.RequestData["Key"]]+"="+Modifier
    return Text
