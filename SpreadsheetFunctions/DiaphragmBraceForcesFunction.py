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
                    SlopeSentivity=1
                    JointForcesResults=AnalysisResultsHooks.GetLoadResultsForObject(ModelJointForces,UniqueName,'Joint')
                    for result in JointForcesResults:
                        if(float(result["F1"])!=0):
                            result["Slope"]=round(float(result["F2"])/float(result["F1"]),SlopeSentivity)
                    Slopes=[]
                    if (len(JointForcesResults) > 0):
                        for i,JointForceResult in enumerate(JointForcesResults):
                            if("Slope" in JointForceResult and JointForceResult["Slope"] not in Slopes):
                                Slopes.append(round(JointForceResult["Slope"],SlopeSentivity))
                                Text=""
                                Pt = Point["Coords"]
                                Story = JointForceResult["Story"]
                                Slope=JointForceResult["Slope"]
                                F1=float(JointForceResult["F1"])
                                F2=float(JointForceResult["F2"])
                                OtherResultsWithSameSlope=[x for x in JointForcesResults if "Slope" in x and x["UniqueName"]!=JointForceResult["UniqueName"] and x["Slope"]==Slope]
                                for otherResult in OtherResultsWithSameSlope:
                                    F1+=float(otherResult["F1"])
                                    F2+=float(otherResult["F2"])
                                Resultant=((F1**2)+(F2**2))**0.5
                                if(Resultant!=0):
                                    #normalize and reverse by resultant
                                    F1reverse=-F1/Resultant
                                    F2reverse=-F2/Resultant
                                    for j in (range(i)):
                                        Text+="\n\n"
                                    Text+=str(round(Resultant,statesAllRequests.RequestDecimalPlaces))
                                    Color=CheckIfBraceIsAboveOrBelow(Story)
                                    statesAllRequests.OutputSheets[statesAllRequests.RequestNameFormat1].append(JointForceResult)
                                    statesAllRequests.PlotTable.append({"Pt":Pt,"F1":F1reverse,"F2":F2reverse,"Resultant":Resultant,"Text":Text,"Color":Color})

def CheckIfBraceIsAboveOrBelow(Story):
    if(Story==statesAllRequests.RequestViewLabel):
        Color="blue"
    else:
        Color="red"
    return Color