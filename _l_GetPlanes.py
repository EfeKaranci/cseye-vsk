import states.statesAllRequests as statesAllRequests
import Planes.PlaneFunctionsHooks as PlaneFunctions
import _m_GetAllSelectedPoints as _m_GetAllSelectedPoints

def GetPlanes():
    for Request in statesAllRequests.Requests:
        RequestViewType,RequestViewLabel,RequestGridSystem=Request['ViewType'],Request['ViewLabels'],Request['GridSystem']
        if not ViewHasAlreadyBeenProcessed(RequestViewType,RequestViewLabel,RequestGridSystem):
            ViewPlane=PlaneFunctions.GetViewPlane(RequestViewType,RequestViewLabel,RequestGridSystem)
            statesAllRequests.ViewPlanesForAllRequests.append(
                {'ViewType':RequestViewType,
                 'ViewLabels':RequestViewLabel,
                 'GridSystem':RequestGridSystem,
                 'PlaneEquation':ViewPlane})
    print("l")
    _m_GetAllSelectedPoints.GetAllSelectedPoints()

def ViewHasAlreadyBeenProcessed(RequestViewType,RequestViewLabel,RequestGridSystem):
    if any(View["ViewType"] == RequestViewType and
               View['ViewLabels'] == RequestViewLabel and
               View["GridSystem"] == RequestGridSystem
           for View in statesAllRequests.ViewPlanesForAllRequests):
        return True
    else:
        return False