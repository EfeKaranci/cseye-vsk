import states.statesAllRequests as statesAllRequests
import _g_GetRequiredCSITablesList as getRequiredCSITablesList
import Hooks.CSIHooks as CSIHooks
def processRequests(selected_requests,outputFilePath,outputFolderPath,units,posViewTolerance,negViewTolerance):
    #error logic if no file name is provided
    CSIHooks.getModel()
    statesAllRequests.Requests=selected_requests
    statesAllRequests.DataTypesRequested = list(set([row["DataType"] for row in selected_requests]))
    statesAllRequests.ViewTypesRequested = list(set([row["ViewType"] for row in selected_requests]))
    statesAllRequests.LoadResultsRequested = list(set([row["LoadCase"] for row in selected_requests]))
    statesAllRequests.OutputName = outputFilePath
    statesAllRequests.OutputFolder = outputFolderPath
    statesAllRequests.SelectedUnits = units
    statesAllRequests.PosViewTolerance = posViewTolerance
    statesAllRequests.NegViewTolerance = negViewTolerance
    getRequiredCSITablesList.GetCSITablesList()
