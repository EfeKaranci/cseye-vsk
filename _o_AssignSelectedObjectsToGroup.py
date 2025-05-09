import random
import string
alphabet = string.ascii_letters + string.digits
import _p_GetCSITables as _p_GetCSITables
def AssignSelectedObjectsToGroup():
        #statesAllRequests.ObjectsGroupName=random_string()
        #statesAllRequests.SapModel.GroupDef.SetGroup(statesAllRequests.ObjectsGroupName)
        """
        for PointName in statesAllRequests.SelectedPointNamesForAllRequests:
                statesAllRequests.SapModel.PointObj.SetGroupAssign(PointName, statesAllRequests.ObjectsGroupName)
        for FrameName in statesAllRequests.SelectedFrameNamesForAllRequests:
                statesAllRequests.SapModel.FrameObj.SetGroupAssign(FrameName, statesAllRequests.ObjectsGroupName)
        for FloorName in statesAllRequests.SelectedFloorNamesForAllRequests:
                statesAllRequests.SapModel.AreaObj.SetGroupAssign(FloorName, statesAllRequests.ObjectsGroupName)
        """
        #Exceptional Cases When you need results from elements not in view
        #DIAPHRAGM FORCES
        print("o")
        _p_GetCSITables.GetRequestedTables()
        
def random_string(length=6):
    alphabet = string.ascii_letters + string.digits
    return ''.join(random.choices(alphabet, k=length))