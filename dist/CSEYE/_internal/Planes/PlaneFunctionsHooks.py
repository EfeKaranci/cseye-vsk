import states.statesAllRequests as statesAllRequests
import numpy as np
import copy

def GetViewPlane(RequestViewType,RequestViewLabel,RequestGridSystem):
    if  (RequestViewType == "Story"):
        return GetViewPlaneStory(RequestViewLabel)
    elif  (RequestViewType == "Elevation"):
        return GetViewPlaneElevation(RequestViewLabel,RequestGridSystem)

def GetViewPlaneStory(RequestViewLabel):
    BaseElevation,IsTheBaseViewRequested = GetBaseElevation(RequestViewLabel)
    SelectedStoryHeight = float(BaseElevation)
    if(not IsTheBaseViewRequested):
        # Reverse List and sum heights to get elvation
        StoryDefinitionsReversed = copy.deepcopy(statesAllRequests.StoryDefinitions)
        StoryDefinitionsReversed.reverse()
        for story in StoryDefinitionsReversed:
            StoryHeight = story['Height']
            SelectedStoryHeight += float(StoryHeight)
            if story['Story'] == RequestViewLabel:
                break  # Exit the loop when the value is found
        # Construct plane
    A, B, C = 0, 0, 1  # Normal vector points along Z-axis
    D = -SelectedStoryHeight  # Plane equation: z = Height
    return {"A": A, "B": B, "C": C, "D": D}

def GetBaseElevation(RequestViewLabel):
    BaseElevation = statesAllRequests.TowerAndBaseDefinitions[0]['BSElev']
    BaseName = statesAllRequests.TowerAndBaseDefinitions[0]['BSName']
    IsTheBaseViewRequested =  (RequestViewLabel==BaseName)
    return BaseElevation, IsTheBaseViewRequested

def GetViewPlaneElevation(RequestViewLabel,RequestGridSystem):
    Gridline = next((row for row in statesAllRequests.GridDefinitions if row['ID'] == RequestViewLabel and row['Name'] == RequestGridSystem), None)
    LineType = Gridline['LineType'] if('LineType' in Gridline) else None
    Ordinate = Gridline['Ordinate'] if('Ordinate' in Gridline) else None
    GridX1 = Gridline['X1'] if('X1' in Gridline) else None
    GridY1 = Gridline['Y1'] if('Y1' in Gridline) else None
    GridX2 = Gridline['X2'] if('X2' in Gridline) else None
    GridY2 = Gridline['Y2'] if('Y2' in Gridline) else None
    if (LineType == "General (Cartesian)"):
        return GetPlaneLineGeneral(float(GridX1), float(GridY1), float(GridX2), float(GridY2),RequestGridSystem)
    else:
        return GetPlaneLineOrdinate(LineType, float(Ordinate),RequestGridSystem)

def DefinePlane(RotatedLine):
    a = RotatedLine["a"]
    b = RotatedLine["b"]
    c = RotatedLine["c"]
    # Extrude vertically by adding z with coefficient 0.
    RotatedPlane={"A": a, "B": b, "C": 0, "D": c}
    return RotatedPlane

def rotate_point(x, y, Ox, Oy, Rz_deg):
    # Convert angle to radians
    theta = np.radians(Rz_deg)
    # Translate point to origin
    dx = x - Ox
    dy = y - Oy
    # Apply rotation matrix
    x_rot = dx * np.cos(theta) - dy * np.sin(theta)
    y_rot = dx * np.sin(theta) + dy * np.cos(theta)
    # Translate point back
    return x_rot + Ox, y_rot + Oy

def GetRotatedLine(TranslatedLine, Ox_new, Oy_new, Oz_new, Rz_deg):
    a = TranslatedLine["a"]
    b = TranslatedLine["b"]
    c = TranslatedLine["c"]
    # Find two distinct points on the line.
    # Case 1: If the line is not vertical (|b| > small epsilon)
    eps = 1e-8
    if abs(b) > eps:
        # Choose x = 0
        x1 = 0
        y1 = -c / b
        # Choose x = 1
        x2 = 1
        y2 = -(a * x2 + c) / b
    else:
        # The line is vertical: a*x + c = 0  => x = -c/a.
        x1 = -c / a
        y1 = 0
        x2 = -c / a
        y2 = 1
    # Rotate both points about (Ox_new, Oy_new)
    x1r, y1r = rotate_point(x1, y1, Ox_new, Oy_new, Rz_deg)
    x2r, y2r = rotate_point(x2, y2, Ox_new, Oy_new, Rz_deg)
    # Compute new line coefficients from the rotated points.
    # The line through (x1r, y1r) and (x2r, y2r) has:
    # a_new = y1r - y2r, b_new = x2r - x1r, and c_new = x1r*y2r - x2r*y1r.
    a_new = y1r - y2r
    b_new = x2r - x1r
    c_new = x1r * y2r - x2r * y1r
    RotatedLine={"a": a_new, "b": b_new, "c": c_new}
    return DefinePlane(RotatedLine)

def GetTranslatedLine(PlaneLine,RequestGridSystem):
    #Get grid transformation

    GridSystemData = next((x for x in statesAllRequests.GridSystems if x["Name"] == RequestGridSystem), None)
    Ux, Uy, Rz_deg = float(GridSystemData["Ux"]), float(GridSystemData["Uy"]), float(GridSystemData["Rz"])
    Ox,Oy,Oz=Ux,Uy,0
    ###Translate line horizontally
    a, b, c = PlaneLine['a'], PlaneLine['b'], PlaneLine['c']
    # Calculate the new c value after translation
    new_c = c + a * Ux + b * Uy
    # Return the new line equation with translated coefficients
    TranslatedLine = {"a": a, "b": b, "c": new_c}
    return GetRotatedLine(TranslatedLine,Ox,Oy,Oz,Rz_deg)

def GetPlaneLineGeneral(X1, Y1, X2, Y2,RequestGridSystem):
    # Calculate the slope m
    if(X2 - X1 != 0):
        m = (Y2 - Y1) / (X2 - X1)
        b = Y1 - m * X1
        # Return the equation in the form ax + by + c = 0, so we rearrange y = mx + b
        # This gives us m * x - y + b = 0
        PlaneLine = {"a": m, "b": -1, "c": b}
    else:
        PlaneLine = {"a": 1, "b": 0, "c": -X1}
    # Calculate the y-intercept b
    return GetTranslatedLine(PlaneLine,RequestGridSystem)

def GetPlaneLineOrdinate(LineType, Ordinate,RequestGridSystem):
    if LineType == "X (Cartesian)":
        # Vertical line, x = Ordinate
        PlaneLine = {"a": 1, "b": 0, "c": -Ordinate}  # x = Ordinate
        return GetTranslatedLine(PlaneLine,RequestGridSystem)
    elif LineType == "Y (Cartesian)":
        PlaneLine = {"a": 0, "b": 1, "c": -Ordinate}  # y = Ordinate
        return GetTranslatedLine(PlaneLine,RequestGridSystem)
    else:
        raise ValueError("Invalid LineType. Use 'X (Cartesian)' or 'Y (Cartesian)'.")