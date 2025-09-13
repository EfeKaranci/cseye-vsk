import states.statesAllRequests as statesAllRequests

def GetLoadResultsForObject(ResultsTable,ObjectId,ResultsIdKey):
    if  (statesAllRequests.RequestLoadStep == ""):
        Results = [x for x in ResultsTable if ResultsIdKey in x
                    and x[ResultsIdKey] == ObjectId and x['OutputCase'] in statesAllRequests.RequestLoadCases]
        # if user requested results for load with max and min step but did not select envelope option
    elif  (statesAllRequests.RequestLoadStep.lower() in ["max", "min", "abs max"]):
        if(statesAllRequests.RequestIsEnvelope=="No"):
            Results = [x for x in ResultsTable if ResultsIdKey in x
                       and x[ResultsIdKey] == ObjectId and x['OutputCase'] in statesAllRequests.RequestLoadCases and x['StepType']!=None and x['StepType'].lower() == statesAllRequests.RequestLoadStep]
        # if user requested results for load with max and min step but did not select envelope option
        elif  (statesAllRequests.RequestIsEnvelope=="Yes"):
            Results = [x for x in ResultsTable if ResultsIdKey in x
                       and x[ResultsIdKey] == ObjectId and x['OutputCase'] in statesAllRequests.RequestLoadCases]
    else:
        Results = [x for x in ResultsTable if ResultsIdKey in x
                       and x[ResultsIdKey] == ObjectId and x['OutputCase'] in statesAllRequests.RequestLoadCases and 'StepNumber' in x and x['StepNumber'] == statesAllRequests.RequestLoadStep]
    return Results

def GetResultsForLoadCase(ResultsTable):
    if  (statesAllRequests.RequestLoadStep == ""):
        Results = [x for x in ResultsTable if x['OutputCase'] in statesAllRequests.RequestLoadCases]
        # if user requested results for load with max and min step but did not select envelope option
    elif  (statesAllRequests.RequestLoadStep.lower() in ["max", "min","abs max"]):
        if(statesAllRequests.RequestIsEnvelope=="No"):
            Results = [x for x in ResultsTable if x['OutputCase'] in statesAllRequests.RequestLoadCases and x['StepType']!=None and x['StepType'].lower() == statesAllRequests.RequestLoadStep]
        # if user requested results for load with max and min step but did not select envelope option
        elif  (statesAllRequests.RequestIsEnvelope=="Yes"):
            Results = [x for x in ResultsTable if x['OutputCase'] in statesAllRequests.RequestLoadCases]
    else:
        Results = [x for x in ResultsTable if x['OutputCase'] in statesAllRequests.RequestLoadCases and 'StepNumber' in x and x['StepNumber'] == statesAllRequests.RequestLoadStep]
    return Results

def GetGoverningResultForObject(Results,RequestedDataKey):
    if(statesAllRequests.RequestIsEnvelope=="No" and len(Results)==1):
        Result=Results[0]
    elif(statesAllRequests.RequestIsEnvelope=="Yes"):
        if(statesAllRequests.RequestLoadStep=="max"):
            Max=max([float(x[RequestedDataKey]) for x in Results])
            Result=next((x for x in Results if float(x[RequestedDataKey]) == Max), None)
        elif(statesAllRequests.RequestLoadStep=="min"):
            Min=min([float(x[RequestedDataKey]) for x in Results])
            Result=next((x for x in Results if float(x[RequestedDataKey]) == Min), None)
        elif(statesAllRequests.RequestLoadStep=="abs max"):
            Min=min([float(x[RequestedDataKey]) for x in Results])
            Max=max([float(x[RequestedDataKey]) for x in Results])
            AbsMax=max(abs(Min),abs(Max))
            if(AbsMax==abs(Min)):
                Result=next((x for x in Results if float(x[RequestedDataKey]) == Min), None)
            else:
                Result=next((x for x in Results if float(x[RequestedDataKey]) == Max), None)
    return Result