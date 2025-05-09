import states.statesAllRequests as statesAllRequests
def GetSelectedPoints():
    for Point in statesAllRequests.SelectedPointsForAllRequests:
        PtPlanes=Point['PtPlanes']
        RequestedPlane=next((Plane for Plane in PtPlanes if Plane['ViewType']==statesAllRequests.RequestViewType and
                                                            Plane['ViewLabels'] == statesAllRequests.RequestViewLabel and
                                                            Plane['GridSystem'] == statesAllRequests.RequestGridSystem), None)
        if(RequestedPlane!=None):
            UniqueName=Point["UniqueName"]
            Story=Point["Story"]
            Coords=RequestedPlane["Coords"]
            statesAllRequests.SelectedPointsForCurrentRequest.append({"UniqueName":UniqueName, "Story":Story,"Coords":Coords})
    statesAllRequests.SelectedPointNamesForCurrentRequest = [x['UniqueName'] for x in statesAllRequests.SelectedPointsForCurrentRequest]