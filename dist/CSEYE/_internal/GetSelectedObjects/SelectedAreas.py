import states.statesAllRequests as statesAllRequests
import Hooks.BasicHooks as BasicHooks
def GetSelectedAreas():
    for floor in statesAllRequests.SelectedFloorsForAllRequests:
        UniqueName=floor['UniqueName']
        PtNames=floor['PtNames']
        if(set(PtNames).issubset(statesAllRequests.SelectedPointNamesForCurrentRequest)):
            PtsData=[BasicHooks.GetPointByName(x) for x in PtNames]
            Coords=[x["Coords"] for x in PtsData]
            statesAllRequests.SelectedAreasForCurrentRequest.append({"UniqueName":UniqueName,"Coords":Coords})