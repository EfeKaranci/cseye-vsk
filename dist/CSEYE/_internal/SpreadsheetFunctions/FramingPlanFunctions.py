import states.statesAllRequests as statesAllRequests
import numpy as np
def GetFramingPlan():
    if(statesAllRequests.RequestData=="Frames"):
        FrameSectionProperties=statesAllRequests.SelectedCSITables["Frame Assignments - Section Properties"]
        for Frame in statesAllRequests.SelectedFramesForCurrentRequest:
            UniqueName=Frame["UniqueName"]
            if(statesAllRequests.RequestGroup=="" or UniqueName in statesAllRequests.RequestGroupFrames):
                SectProp = next((x for x in FrameSectionProperties if x["UniqueName"]==UniqueName), None)
                if(SectProp!=None):
                    SectProp=SectProp["SectProp"]
                    PtI, PtJ = Frame["Pt2dI"],Frame["Pt2dJ"]
                    mid = (PtI + PtJ) / 2
                    statesAllRequests.PlotTable.append({"Pt2d":mid, "Text":SectProp})
    if(statesAllRequests.RequestData=="Areas"):
        AreaSectionProperties = statesAllRequests.SelectedCSITables["Area Assignments - Section Properties"]
        for Floor in statesAllRequests.SelectedAreasForCurrentRequest:
            UniqueName=Floor["UniqueName"]
            if(statesAllRequests.RequestGroup=="" or UniqueName in statesAllRequests.RequestGroupAreas):
                SectProp = next((x for x in AreaSectionProperties if x["UniqueName"]==UniqueName), None)
                if(SectProp!=None): 
                    SectProp=SectProp["SectProp"]
                    Pts=Floor["Coords"]
                    x = [x[0] for x in Pts]
                    y = [x[1] for x in Pts]
                    # roll so that x[i],y[i] pairs with x[i+1],y[i+1], wrapping around
                    x1 = np.roll(x, -1)
                    y1 = np.roll(y, -1)
                    # Compute the signed area (twice the area actually)
                    a = x * y1 - x1 * y
                    A = a.sum() / 2.0
                    if np.isclose(A, 0):
                        raise ValueError("Polygon has zero area, centroid is undefined")
                    # Compute centroid coordinates
                    Cx = ((x + x1) * a).sum() / (6.0 * A)
                    Cy = ((y + y1) * a).sum() / (6.0 * A)
                    Centroid=np.array([Cx, Cy])
                    statesAllRequests.PlotTable.append({"Pt2d":Centroid, "Text":SectProp})
