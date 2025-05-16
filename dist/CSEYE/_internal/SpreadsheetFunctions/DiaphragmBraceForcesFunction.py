import states.statesAllRequests as statesAllRequests
import Hooks.BasicHooks as BasicHooks
import Hooks.AnalysisResultsHooks as AnalysisResultsHooks

def GetDiaphragmBraceFoces():
    ModelJointForces = statesAllRequests.SelectedCSITables["Element Joint Forces - Frame"]
    ModelJointForces=[x for x in ModelJointForces if "D" in x["Frame"]]
    JointsWithResults=[x['Joint'] for x in ModelJointForces]
    LoopedPoints=[]
    for Point in statesAllRequests.SelectedPointsForCurrentRequest:
        UniqueName=Point['UniqueName']
        if(statesAllRequests.RequestGroup=="" or UniqueName in statesAllRequests.RequestGroupPoints):
            if(UniqueName in JointsWithResults):
                if(UniqueName not in LoopedPoints):
                    LoopedPoints.append(UniqueName)
                    JointForcesResults=AnalysisResultsHooks.GetLoadResultsForObject(ModelJointForces,UniqueName,'Joint')
                    if (len(JointForcesResults) > 0):
                        for i,JointForceResult in enumerate(JointForcesResults):
                            Text=""
                            Pt = Point["Coords"]
                            Story = JointForceResult["Story"]
                            F1=float(JointForceResult["F1"])
                            F2=float(JointForceResult["F2"])
                            Resultant=((F1**2)+(F2**2))**0.5
                            if(Resultant!=0):
                                #normalize and reverse by resultant
                                F1reverse=-F1/Resultant
                                F2reverse=-F2/Resultant
                                for j in (range(i)):
                                    Text+="\n\n"
                                Text+=str(round(Resultant,statesAllRequests.RequestDecimalPlaces))+"("+UniqueName+")"
                                Color=CheckIfBraceIsAboveOrBelow(Story)
                                statesAllRequests.OutputSheets[statesAllRequests.RequestNameFormat1].append(JointForceResult)
                                statesAllRequests.PlotTable.append({"Pt":Pt,"F1":F1reverse,"F2":F2reverse,"Text":Text,"Color":Color})

def CheckIfBraceIsAboveOrBelow(Story):
    if(Story==statesAllRequests.RequestViewLabel):
        Color="blue"
    else:
        Color="red"
    return Color