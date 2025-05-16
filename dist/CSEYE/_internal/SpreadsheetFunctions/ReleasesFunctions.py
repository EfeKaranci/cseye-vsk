import states.statesAllRequests as statesAllRequests

def GetReleases():
    ModelReleases=statesAllRequests.SelectedCSITables["Frame Assignments - Releases and Partial Fixity"]
    RequestedDataKeysI=RequestedDataDict[statesAllRequests.RequestData]["IKeys"]
    RequestedDataKeysJ=RequestedDataDict[statesAllRequests.RequestData]["JKeys"]
    for index,Frame in enumerate(statesAllRequests.SelectedFramesForCurrentRequest):
        UniqueName,Story=Frame["UniqueName"],Frame["Story"]
        if(statesAllRequests.RequestGroup=="" or UniqueName in statesAllRequests.RequestGroupFrames):
            ReleaseData=next((x for x in ModelReleases if x["UniqueName"] == UniqueName), None)
            if(ReleaseData!=None):
                EndIReleases=[key for key in RequestedDataKeysI if ReleaseData[key]=="Yes"]
                EndJReleases=[key for key in RequestedDataKeysJ if ReleaseData[key]=="Yes"]
                if(len(EndIReleases)>0 or len(EndJReleases)>0):
                    #Mark frames with both releases as red and those with only one side as blue
                    Color="red" if (len(EndIReleases)>0 and len(EndJReleases)>0) else "green"
                    statesAllRequests.SelectedFramesForCurrentRequest[index]["Color"]=Color
                    #Get release text
                    EndIText=GetEndText(EndIReleases)
                    EndJText=GetEndText(EndJReleases)
                    #Get EndPoints
                    PtIScaled,PtJScaled=GetScaledEndPoints(Frame)
                    statesAllRequests.OutputSheets[statesAllRequests.RequestNameFormat1].append(ReleaseData)
                    statesAllRequests.PlotTable.append({"Pt2d":PtIScaled,"Text":EndIText})
                    statesAllRequests.PlotTable.append({"Pt2d":PtJScaled,"Text":EndJText})

RequestedDataDict={"P": {"IKeys":["PI"],"JKeys":["PJ"]},
                   "V2":{"IKeys":["V2I"],"JKeys":["V2J"]},
                    "V3":{"IKeys":["V3I"],"JKeys":["V3J"]},
                   "T":{"IKeys":["TI"],"JKeys":["TJ"]},
                    "M2":{"IKeys":["M2I"],"JKeys":["M2J"]},
                   "M3":{"IKeys":["M3I"],"JKeys":["M3J"]},
                   "All":{"IKeys":["PI","V2I","V3I","TI","M2I","M3I"],"JKeys":["PJ","V2J","V3J","TJ","M2J","M3J"]}}

def GetScaledEndPoints(Frame):
    PtI = Frame["Pt2dI"]
    PtJ = Frame["Pt2dJ"]
    Scale=0.65
    midpoint = (PtI + PtJ) / 2.0
    PtIScaled = midpoint + (PtI - midpoint) * Scale
    PtJScaled = midpoint + (PtJ - midpoint) * Scale
    return PtIScaled, PtJScaled

def GetEndText(ReleaseKeys):
    Text=""
    for index,ReleaseKey in enumerate(ReleaseKeys):
        Text+=ReleaseKey
        if(index!=len(ReleaseKeys)-1):Text+="\n"
    return Text

