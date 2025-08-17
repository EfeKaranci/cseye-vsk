import states.statesAllRequests as statesAllRequests
import _o_AssignSelectedObjectsToGroup as _o_AssignSelectedObjectsToGroup
import states.statesUI as statesUI

def GetAllSelectedFramesAndFloors():
    statesUI.counter+=1
    statesUI.update_status()
    GetSelectedFrames()
    GetSelectedFloors()
    statesAllRequests.SelectedFrameNamesForAllRequests=[x['UniqueName'] for x in statesAllRequests.SelectedFramesForAllRequests]
    statesAllRequests.SelectedFloorNamesForAllRequests=[x['UniqueName'] for x in statesAllRequests.SelectedFloorsForAllRequests]
    statesAllRequests.SelectedNullAreaNamesForAllRequests=[x['UniqueName'] for x in statesAllRequests.SelectedNullAreasForAllRequests]
    print("n")
    _o_AssignSelectedObjectsToGroup.AssignSelectedObjectsToGroup()

def GetSelectedFrames():
    for Frame in statesAllRequests.FrameObjectConnectivity:
        UniqueName=Frame['UniqueName']
        Story=Frame['Story']
        UniquePtI=Frame['UniquePtI']
        UniquePtJ=Frame['UniquePtJ']
        FrameType=Frame['FrameType']
        if (set([UniquePtI,UniquePtJ]).issubset(statesAllRequests.SelectedPointNamesForAllRequests)):
            statesAllRequests.SelectedFramesForAllRequests.append({"UniqueName":UniqueName, "UniquePtI":UniquePtI, "UniquePtJ":UniquePtJ, "Story":Story, "FrameType":FrameType})

def GetSelectedFloors():
    Looped=[]
    for floor in statesAllRequests.FloorObjectConnectivity:
        UniqueName=floor['UniqueName']
        if(UniqueName not in Looped):
            Looped.append(UniqueName)
            PtNames=[]
            floorAllRows=[x for x in statesAllRequests.FloorObjectConnectivity if x['UniqueName'] == UniqueName]
            for row in floorAllRows:
                PtNames.extend([row['UniquePt1'],row['UniquePt2'],row['UniquePt3'],row['UniquePt4']])
            PtNames=[x for x in PtNames if x!=None]
            if all(item in statesAllRequests.SelectedPointNamesForAllRequests for item in PtNames):
                statesAllRequests.SelectedFloorsForAllRequests.append({"UniqueName":UniqueName, "PtNames":PtNames})
    for floor in statesAllRequests.NullAreaObjectConnectivity:
        UniqueName=floor['UniqueName']
        if(UniqueName not in Looped):
            Looped.append(UniqueName)
            PtNames=[]
            floorAllRows=[x for x in statesAllRequests.NullAreaObjectConnectivity if x['UniqueName'] == UniqueName]
            for row in floorAllRows:
                PtNames.extend([row['UniquePt1'],row['UniquePt2'],row['UniquePt3'],row['UniquePt4']])
            PtNames=[x for x in PtNames if x!=None]
            if all(item in statesAllRequests.SelectedPointNamesForAllRequests for item in PtNames):
                statesAllRequests.SelectedNullAreasForAllRequests.append({"UniqueName":UniqueName, "PtNames":PtNames})
