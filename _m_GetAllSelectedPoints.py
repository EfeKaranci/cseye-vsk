import states.statesAllRequests as statesAllRequests
import numpy as np
import math
import copy
import _n_GetAllSelectedFramesAndFloors as _n_GetAllSelectedFramesAndFloors
import states.statesUI as statesUI
import states.statesAllRequests as statesAllRequests
def GetAllSelectedPoints():
    statesUI.counter+=1
    statesUI.update_status()
    GetSelectedPointsForAllRequests()
    statesAllRequests.SelectedPointNamesForAllRequests=[x['UniqueName'] for x in statesAllRequests.SelectedPointsForAllRequests]
    print("m")
    _n_GetAllSelectedFramesAndFloors.GetAllSelectedFramesAndFloors()

def GetSelectedPointsForAllRequests():
    PosDistanceFromPlane,NegDistanceFromPlane = GetMaxAllowedDistanceFromPlane()
    for Point in statesAllRequests.PointObjectConnectivity:
        UniqueName=Point['UniqueName']
        X=float(Point['X'])
        Y=float(Point['Y'])
        Z=float(Point['Z'])
        Story=Point['Story']
        PlanesOnWhichThisPointAppears=[]
        for index,Plane in enumerate(statesAllRequests.ViewPlanesForAllRequests):
            DistanceToPlane = GetDistanceBetweenPointandPlane(X, Y, Z,Plane['PlaneEquation'])
            if ((DistanceToPlane < 0 and abs(DistanceToPlane) < NegDistanceFromPlane) or 
                (DistanceToPlane > 0 and abs(DistanceToPlane) < PosDistanceFromPlane)):
                if ("Origin" not in statesAllRequests.ViewPlanesForAllRequests[index]):
                    #initiate origin for plane
                    statesAllRequests.ViewPlanesForAllRequests[index]["Origin"]=np.array([X, Y, Z], dtype=float)
                Pt = np.array([X, Y, Z], dtype=float)
                PlaneOrigin= statesAllRequests.ViewPlanesForAllRequests[index]["Origin"]
                #Get the points 2d coordinates for this specific plane
                pt2d = to_plane_coords(Pt,PlaneOrigin,Plane['PlaneEquation'])
                #attach the points 2d coordinates to the plane and attach plane to point
                NewPlane=copy.deepcopy(Plane)
                NewPlane['Coords']=pt2d
                PlanesOnWhichThisPointAppears.append(NewPlane)
        if(len(PlanesOnWhichThisPointAppears)>0):
                statesAllRequests.SelectedPointsForAllRequests.append({"UniqueName":UniqueName, "Story":Story, "PtPlanes":PlanesOnWhichThisPointAppears})

def GetMaxAllowedDistanceFromPlane():    
    if (statesAllRequests.DisplacementUnit== "in"):
        PosDistanceFromPlane=float(statesAllRequests.PosViewTolerance)
        NegDistanceFromPlane=float(statesAllRequests.NegViewTolerance)
    elif (statesAllRequests.DisplacementUnit == "ft"):
        PosDistanceFromPlane=float(statesAllRequests.PosViewTolerance) / 12
        NegDistanceFromPlane=float(statesAllRequests.NegViewTolerance) / 12
    return PosDistanceFromPlane,NegDistanceFromPlane

def GetDistanceBetweenPointandPlane(X,Y,Z,PlaneEquation):
    # Deconstruct plane
    A, B, C, D = PlaneEquation["A"], PlaneEquation["B"], PlaneEquation["C"], PlaneEquation["D"]
    numerator = abs(A * X + B * Y + C * Z + D)
    denominator = math.sqrt(A ** 2 + B ** 2 + C ** 2)
    if denominator == 0:
        return 0
    return numerator / denominator

def to_plane_coords(Point,Origin,Plane):
    A = Plane["A"]
    B = Plane["B"]
    C = Plane["C"]
    D = Plane["D"]
    n = np.array([A, B, C], dtype=float)
    n = n / np.linalg.norm(n)
    # Compute vector from the plane's origin to the point.
    diff = Point - Origin
    # Choose the local coordinate system for the plane.
    # If the plane is nearly horizontal:
    if abs(n[2]) > 0.9:
        # Use global x and y
        local_x = np.array([1, 0, 0], dtype=float)
        local_y = np.array([0, 1, 0], dtype=float)
    # If the plane is nearly vertical (normal is roughly in the xy-plane):
    elif abs(n[2]) < 1e-3:
        # Make the local y-axis the global z-axis.
        local_y = np.array([0, 0, 1], dtype=float)
        # Compute local_x to be in the plane: cross(global z, n)
        local_x = np.cross(local_y, n)
        local_x = local_x / np.linalg.norm(local_x)
    else:
        # For other cases, we can choose to follow the vertical convention,
        # i.e. use the global z-axis for local y.
        local_y = np.array([0, 0, 1], dtype=float)
        local_x = np.cross(local_y, n)
        if np.linalg.norm(local_x) < 1e-6:
            # Fallback: use global x-axis then compute local_y accordingly.
            local_x = np.array([1, 0, 0], dtype=float)
            local_y = np.cross(n, local_x)
        local_x = local_x / np.linalg.norm(local_x)
    # Now, project the difference vector onto these basis vectors:

    x_coord = np.dot(diff, local_x)
    y_coord = np.dot(diff, local_y)
    return np.array([x_coord, y_coord])