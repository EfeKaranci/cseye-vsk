import states.statesAllRequests as statesAllRequests
import hooks.basicHooks as BasicHooks
def GetSelectedFrames():
    for Frame in statesAllRequests.SelectedFramesForAllRequests:
        UniqueName=Frame['UniqueName']
        UniquePtI=Frame['UniquePtI']
        UniquePtJ=Frame['UniquePtJ']
        Story=Frame['Story']
        FrameType=Frame['FrameType']
        PtIData = BasicHooks.GetPointByName(UniquePtI)
        if (PtIData != None): Pt2dI = PtIData["Coords"]
        PtJData = BasicHooks.GetPointByName(UniquePtJ)
        if (PtJData != None): Pt2dJ = PtJData["Coords"]
        if (set([UniquePtI,UniquePtJ]).issubset(statesAllRequests.SelectedPointNamesForCurrentRequest)):
            statesAllRequests.SelectedFramesForCurrentRequest.append({"UniqueName":UniqueName,"UniquePtI":UniquePtI,"UniquePtJ":UniquePtJ,"Story":Story,"FrameType":FrameType,"Pt2dI":Pt2dI,"Pt2dJ":Pt2dJ})
        if(FrameType=="Column"):
            if(not set([UniquePtI,UniquePtJ]).issubset(statesAllRequests.SelectedPointNamesForCurrentRequest)):
                if(UniquePtI in statesAllRequests.SelectedPointNamesForCurrentRequest):statesAllRequests.PlanColumns.append({"Pt2d":Pt2dI})
                if(UniquePtJ in statesAllRequests.SelectedPointNamesForCurrentRequest):statesAllRequests.PlanColumns.append({"Pt2d":Pt2dJ})
        if(FrameType=="Brace"):
            if(not set([UniquePtI,UniquePtJ]).issubset(statesAllRequests.SelectedPointNamesForCurrentRequest)):
                if(UniquePtI in statesAllRequests.SelectedPointNamesForCurrentRequest):statesAllRequests.PlanBraces.append({"Pt2d":Pt2dI})
                if(UniquePtJ in statesAllRequests.SelectedPointNamesForCurrentRequest):statesAllRequests.PlanBraces.append({"Pt2d":Pt2dJ})
    print(statesAllRequests.SelectedFramesForCurrentRequest)
