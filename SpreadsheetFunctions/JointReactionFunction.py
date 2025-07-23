import states.statesAllRequests as statesAllRequests
import hooks.AnalysisResultsHooks as AnalysisResultsHooks

def JointReactionFunction():
    ModelReactions=statesAllRequests.SelectedCSITables["Joint Reactions"]
    RequestedDataKey=RequestedDataKeyDict[statesAllRequests.RequestData]
    JointsWithReactionResults=[x['UniqueName'] for x in ModelReactions]
    for Point in statesAllRequests.SelectedPointsForCurrentRequest:
        UniqueName=Point['UniqueName']
        if(statesAllRequests.RequestGroup=="" or UniqueName in statesAllRequests.RequestGroupPoints):
            if(UniqueName in JointsWithReactionResults):
                Pt2d=Point['Coords']
                BaseReactionResults=AnalysisResultsHooks.GetLoadResultsForObject(ModelReactions,UniqueName,'UniqueName')
                if(len(BaseReactionResults)>0):
                    BaseReactionResult = AnalysisResultsHooks.GetGoverningResultForObject(BaseReactionResults, RequestedDataKey)
                    if (BaseReactionResult != None):
                        OutputCase=BaseReactionResult['OutputCase']
                        BaseReactionResult['Controlling Case/Combo']=OutputCase
                        RequestedRxn=float(BaseReactionResult[RequestedDataKey])
                        Text=GetMappedText(UniqueName,RequestedRxn,OutputCase)
                        statesAllRequests.OutputSheets[statesAllRequests.RequestNameFormat1].append(BaseReactionResult)
                        statesAllRequests.PlotTable.append({"Pt2d":Pt2d,"Value":RequestedRxn,"Text":Text})

RequestedDataKeyDict={"FX":"FX","FY":"FX","FZ":"FZ","MX":"MX","MY":"MY","MZ":"MZ"}

def GetMappedText(UniqueName,RequestedReaction,OutputCase):
    MappedReaction = round(RequestedReaction, statesAllRequests.RequestDecimalPlaces)
    MappedReaction = str(MappedReaction)
    Text = "(" + str(UniqueName) + ")" + "\n" + MappedReaction
    if (statesAllRequests.RequestIsEnvelope == "Yes"):
        Text = Text + "\n" + OutputCase
    return Text