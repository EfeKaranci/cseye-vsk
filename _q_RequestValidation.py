import states.statesAllRequests as statesAllRequests
import _r_MappingLoop as _r_MappingLoop
import states.statesUI as statesUI

def RequestValidation():
    statesUI.counter+=1
    statesUI.update_status()
    for i, Request in enumerate(statesAllRequests.Requests):
       pass
    print("q")
    _r_MappingLoop.MappingLoop()

#Validate diaphragm envelope combo selection'
#validate views exist
#validate load combos existde
#validate diaphragm view type