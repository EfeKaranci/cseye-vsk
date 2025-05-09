import states.statesAllRequests as statesAllRequests
import Hooks.AnalysisResultsHooks as AnalysisResultsHooks
def BaseReactionFunction():
    ModelBaseReactions=statesAllRequests.SelectedCSITables["Base Reactions"]
    BaseReactionsForLoadCase=AnalysisResultsHooks.GetResultsForLoadCase(ModelBaseReactions)
    statesAllRequests.OutputSheets[statesAllRequests.RequestNameFormat1]=BaseReactionsForLoadCase
