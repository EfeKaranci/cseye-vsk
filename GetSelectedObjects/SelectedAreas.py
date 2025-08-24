import states.statesAllRequests as statesAllRequests
import hooks.basicHooks as BasicHooks
def GetSelectedAreas():
    for floor in statesAllRequests.SelectedFloorsForAllRequests:
        UniqueName=floor['UniqueName']
        PtNames=floor['PtNames']
        if(set(PtNames).issubset(statesAllRequests.SelectedPointNamesForCurrentRequest)):
            PtsData=[BasicHooks.GetPointByName(x) for x in PtNames]
            if(PtsData!=None):
                Coords=[x["Coords"] for x in PtsData]
                statesAllRequests.SelectedAreasForCurrentRequest.append({"UniqueName":UniqueName,"Coords":Coords})
    for floor in statesAllRequests.SelectedNullAreasForAllRequests:
        UniqueName=floor['UniqueName']
        AreaProperty = [x for x in statesAllRequests.AreaAssignments if x["UniqueName"]==UniqueName]
        PropType=""
        if len(AreaProperty)>0:
            PropType=AreaProperty[0]["PropType"]
        PtNames=floor['PtNames']
        if(set(PtNames).issubset(statesAllRequests.SelectedPointNamesForCurrentRequest)):
            PtsData=[BasicHooks.GetPointByName(x) for x in PtNames]
            if(PtsData!=None):
                Coords=[x["Coords"] for x in PtsData]
                statesAllRequests.SelectedNullAreasForCurrentRequest.append({"UniqueName":UniqueName,"Coords":Coords,"PropType":PropType})