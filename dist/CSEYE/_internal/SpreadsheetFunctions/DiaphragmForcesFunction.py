import states.statesAllRequests as statesAllRequests
import Hooks.AnalysisResultsHooks as AnalysisResultsHooks

def GetDiaphragmForces():
    DiaphragmForces = statesAllRequests.SelectedCSITables["Diaphragm Forces"]
    JointsWithResults=[x['UniqueName'] for x in DiaphragmForces]
    for Point in statesAllRequests.SelectedPointsForCurrentRequest:
        UniqueName=Point['UniqueName']
        if(statesAllRequests.RequestGroup=="" or UniqueName in statesAllRequests.RequestGroupPoints):
            JointForcesResults=AnalysisResultsHooks.GetLoadResultsForObject(DiaphragmForces,UniqueName,'UniqueName')
            if(UniqueName in JointsWithResults):
                Pt = Point["Coords"]
                JointForceResult=JointForcesResults[0]
                XKey=RequestedDataDict[statesAllRequests.RequestData]["XKey"]
                YKey=RequestedDataDict[statesAllRequests.RequestData]["YKey"]
                FX=float(JointForceResult[XKey])
                FY=float(JointForceResult[YKey])
                Resultant=((FX**2)+(FY**2))**0.5
                Color="red"
                if (Resultant != 0):
                    FX = FX/Resultant
                    FY = FY/Resultant
                    Text = str(round(Resultant, statesAllRequests.RequestDecimalPlaces)) + "(" + UniqueName + ")"
                    statesAllRequests.PlotTable.append({"Pt": Pt, "F1": FX, "F2": FY,"Resultant":Resultant,"Text": Text, "Color": Color})
                    statesAllRequests.OutputSheets[statesAllRequests.RequestNameFormat1].append(JointForceResult)
                    # normalize and reverse by resultant


RequestedDataDict={"Applied Force": {"XKey":"FXA","YKey":"FYA"},
                    "Reactive Force":{"XKey":"FXR","YKey":"FYR"},
                    "Diaphragm Force":{"XKey":"FXDia","YKey":"FYDia"}}

"""

                    if(Resultant!=0):
                        #normalize and reverse by resultant
                        F1reverse=-F1/Resultant
                        F2reverse=-F2/Resultant
                        for j in (range(i)):
                            Text+="\n\n"
                        Text+=str(round(Resultant,statesAllRequests.RequestDecimalPlaces))+"("+UniqueName+")"
                        Color=""
                        statesAllRequests.PlotTable.append({"Pt":Pt,"F1":F1reverse,"F2":F2reverse,"Text":Text,"Color":Color})
"""