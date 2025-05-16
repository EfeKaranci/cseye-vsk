import states.statesAllRequests as statesAllRequests
import numpy as np
def GetFrameLoadAssignmentsDistributed():
    FrameLoadsAssignmentsDistributed = statesAllRequests.SelectedCSITables["Frame Loads Assignments - Distributed"]
    FramesWithDistributedLoad = [x["UniqueName"] for x in FrameLoadsAssignmentsDistributed]
    for index,Frame in enumerate(statesAllRequests.SelectedFramesForCurrentRequest):
        UniqueName=Frame["UniqueName"]
        if(UniqueName in FramesWithDistributedLoad):
            FrameLoadProperty = next((x for x in FrameLoadsAssignmentsDistributed if x["UniqueName"] == UniqueName), None)
"""
    for index,Floor in enumerate(statesAllRequests.SelectedAreasForCurrentRequest):
        UniqueName=Floor["UniqueName"]
        if(UniqueName in AreasWithUniformLoad):
            AreaProperty = next((x for x in AreaLoadAssignmentsUniform if x["UniqueName"]==UniqueName), None)
            Pts=Floor["Coords"]
            Dir=AreaProperty["Dir"]
            Centroid=GetCentroid(Pts)
            Load=float(AreaProperty["Load"])
            if(Load!=0):statesAllRequests.SelectedAreasForCurrentRequest[index]["Color"]="red"
            Text=str(Load)+"("+Dir+")"
            statesAllRequests.PlotTable.append({"Pt2d":Centroid,"Text":Text})
"""