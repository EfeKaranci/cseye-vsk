import states.statesAllRequests as statesAllRequests
import numpy as np
def GetAreaLoadAssignmentsUniform():
    AreaLoadAssignmentsUniform = statesAllRequests.SelectedCSITables["Area Load Assignments - Uniform"]
    AreasWithUniformLoad = [x["UniqueName"] for x in AreaLoadAssignmentsUniform]
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

def GetCentroid(Pts):
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
    Centroid = np.array([Cx, Cy])
    return Centroid
"""
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
"""