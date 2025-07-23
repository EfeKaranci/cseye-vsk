import states.statesAllRequests as statesAllRequests
import hooks.AnalysisResultsHooks as AnalysisResultsHooks

def GetStoryForcesSpreadsheet():
    ModelStoryForces=statesAllRequests.SelectedCSITables["Story Forces"]
    StoryForcesForLoadCase=AnalysisResultsHooks.GetResultsForLoadCase(ModelStoryForces)
    statesAllRequests.OutputSheets[statesAllRequests.RequestNameFormat1]=StoryForcesForLoadCase
