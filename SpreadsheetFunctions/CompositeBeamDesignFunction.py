import states.statesAllRequests as statesAllRequests

def CompositeBeamDesignFunction():
    BeamDesignResults = statesAllRequests.SelectedCSITables["Composite Beam Design Summary - AISC 360-16"]
    print(BeamDesignResults)
    print("Composite Beam Design")