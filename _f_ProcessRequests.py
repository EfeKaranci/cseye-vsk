import states.statesAllRequests as statesAllRequests
import _g_GetRequiredCSITablesList as getRequiredCSITablesList
import hooks.csiHooks as CSIHooks
import states.statesUI as statesUI
import _u_Reset as _u_Reset
def processRequests(selected_requests,outputFilePath,outputFolderPath,units,posViewTolerance,negViewTolerance):
    _u_Reset.ResetGeneralStates2()
    statesUI.counter+=1
    statesUI.update_status()
    CSIHooks.getModel()
    statesAllRequests.Requests=selected_requests
    statesAllRequests.DataTypesRequested = list(set([row["DataType"] for row in selected_requests]))
    statesAllRequests.ViewTypesRequested = list(set([row["ViewType"] for row in selected_requests]))
    statesAllRequests.LoadResultsRequested = list(set([row["LoadCase"] for row in selected_requests]))
    statesAllRequests.OutputName = outputFilePath
    statesAllRequests.OutputFolder = outputFolderPath
    statesAllRequests.SelectedUnits = units
    statesAllRequests.PosViewTolerance = max(posViewTolerance,6)
    statesAllRequests.NegViewTolerance = max(negViewTolerance,6)
    getRequiredCSITablesList.GetCSITablesList()
