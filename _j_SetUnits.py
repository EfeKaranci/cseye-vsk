import states.statesAllRequests as statesAllRequests
import database.csiTables as csiTables
import _f_ProcessRequests as _f_ProcessRequests
import _k_ModifyRequests as _k_ModifyRequests

def SetModelUnits():
    statesAllRequests.SapModel.SetPresentUnits(csiTables.UnitsKey[statesAllRequests.SelectedUnits])
    Units= statesAllRequests.SelectedUnits.split("_")
    #deconstruct
    statesAllRequests.DisplacementUnit=Units[1]
    print("j")
    _k_ModifyRequests.ModifyRequests()