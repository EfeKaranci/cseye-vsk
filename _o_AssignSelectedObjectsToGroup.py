import random
import string
alphabet = string.ascii_letters + string.digits
import _p_GetCSITables as _p_GetCSITables
import states.statesUI as statesUI
import states.statesAllRequests as statesAllRequests

def AssignSelectedObjectsToGroup():
        statesUI.counter+=1
        statesUI.update_status()
 
        #Exceptional Cases When you need results from elements not in view
        #DIAPHRAGM FORCES
        print("o")
        _p_GetCSITables.GetRequestedTables()
        
def random_string(length=6):
    alphabet = string.ascii_letters + string.digits
    return ''.join(random.choices(alphabet, k=length))