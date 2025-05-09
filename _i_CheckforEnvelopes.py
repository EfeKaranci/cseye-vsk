import states.statesAllRequests as statesAllRequests
import _j_SetUnits as _j_SetUnits
def CheckForEnvelopes():
    CheckIfComboIsEnvelope()
    statesAllRequests.SapModel.DatabaseTables.SetLoadPatternsSelectedForDisplay(statesAllRequests.LoadResultsRequested);
    statesAllRequests.SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(statesAllRequests.LoadResultsRequested);
    statesAllRequests.SapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay(statesAllRequests.LoadResultsRequested);
    print("i")
    _j_SetUnits.SetModelUnits()

def CheckIfComboIsEnvelope():
    #Get the actual envelope combos from the model
    ModelEnvelopeCombos = [x["Name"] for x in statesAllRequests.LoadCombinationDefinitions if x["Type"] == "Envelope"]
    EnvelopeCombosRequested=[x for x in statesAllRequests.LoadResultsRequested if x in ModelEnvelopeCombos]
    ModifyRequestsToSayIsOrIsNotEnvelope(EnvelopeCombosRequested)
    #Create a key of Envelope Combos for future use
    for index,EnvelopeCombo in enumerate(EnvelopeCombosRequested):
        ConstituentCombos=[x["LoadName"] for x in statesAllRequests.LoadCombinationDefinitions if x["Name"] == EnvelopeCombo]
        statesAllRequests.EnvelopeComboKey[EnvelopeCombo]=ConstituentCombos
        statesAllRequests.LoadResultsRequested.extend(ConstituentCombos)
    #make sure you have unique list of combos
    statesAllRequests.LoadResultsRequested=list(set(statesAllRequests.LoadResultsRequested))

def ModifyRequestsToSayIsOrIsNotEnvelope(EnvelopeCombosRequested):
    for index,Request in enumerate(statesAllRequests.Requests):
        if(Request['LoadCase'] in EnvelopeCombosRequested):
            statesAllRequests.Requests[index]['IsEnvelope']= "Yes"
            if(Request['LoadStep'].lower() not in ["max","min"]):
                statesAllRequests.Requests[index]['LoadStep']= "max"
        else:
            statesAllRequests.Requests[index]['IsEnvelope']= "No"