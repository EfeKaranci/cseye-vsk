import states.statesAllRequests as statesAllRequests
import copy
import _l_GetPlanes as _l_GetPlanes
import states.statesUI as statesUI

def ModifyRequests():
    statesUI.counter+=1
    statesUI.update_status()
    NewRequests=[]
    for i,Request in enumerate(statesAllRequests.Requests):
        ViewLabels=Request['ViewLabels'][0].split(";")
        for ViewLabel in ViewLabels:
            ViewLabel=ViewLabel.strip()
            NewRequest=copy.deepcopy (statesAllRequests.Requests[i])
            NewRequest['ViewLabels']=ViewLabel
            NewRequests.append(NewRequest)
    statesAllRequests.Requests=NewRequests
    print("k")
    _l_GetPlanes.GetPlanes()
