#CONFIG
import states.statesAllRequests as statesAllRequests
#SPREADSHEET FUNCTIONS
import SpreadsheetFunctions.JointReactionFunction as JointReactionFunction
import SpreadsheetFunctions.DiaphragmForcesFunction as DiaphragmForcesFunction
import SpreadsheetFunctions.DiaphragmBraceForcesFunction as DiaphragmBraceForcesFunction
import SpreadsheetFunctions.EndForcesFunction as EndForcesFunction
import SpreadsheetFunctions.FramingPlanFunctions as FramingPlanFunctions
import SpreadsheetFunctions.ModifierFunctions as ModifierFunctions
import SpreadsheetFunctions.ReleasesFunctions as ReleasesFunctions
import SpreadsheetFunctions.LoadAssigns.FrameLoadAssignmentsDistributed as FrameLoadAssignmentsDistributed
import SpreadsheetFunctions.LoadAssigns.AreaLoadAssignmentsUniform as AreaLoadAssignmentsUniform
import SpreadsheetFunctions.JointDisplacementFunction as JointDisplacementFunction
import SpreadsheetFunctions.JointDriftFunction as JointDriftFunction
import SpreadsheetFunctions.MaxFrameForcesFunction as MaxFrameForcesFunction
import SpreadsheetFunctions.SteelDesignFunctions as SteelDesignFunctions
import SpreadsheetFunctions.ModalPropertiesFunction as ModalPropertiesFunction
import SpreadsheetFunctions.BaseReactionFunction as BaseReactionFunction
import SpreadsheetFunctions.StoryForcesFunction as StoryForcesFunction
#HOOK MODULES
import GetSelectedObjects.SelectedPoints as SelectedPointsForCurrentRequest
import GetSelectedObjects.SelectedFrames as SelectedFrames
import GetSelectedObjects.SelectedAreas as SelectedAreasForCurrentRequest
#MAIN MODULES
import _s_SetRequestStates as _s_SetRequestStates
import _v_WriteFiles as _v_WriteFiles
import _u_Reset as _u_Reset
#PLOTTING
import PlottingFunctions.PlotStructure as PlotStructure
import PlottingFunctions.PlotPointParameters as PlotPointParameters
import PlottingFunctions.PlotColumnsAndBraces as PlotColumnsAndBraces
import PlottingFunctions.PlotText as PlotText
import PlottingFunctions.PlotVectors as PlotVectors
import PlottingFunctions.PlotVectorsAndPointParameters as PlotVectorsAndPointParameters
import states.statesUI as statesUI
def MappingLoop():
    statesUI.counter+=1
    statesUI.update_status()
    for i,Request in enumerate(statesAllRequests.Requests):
        _s_SetRequestStates.SetRequestStates(Request,i)
        #initialize sheets
        statesAllRequests.OutputSheets[statesAllRequests.RequestNameFormat1] = []
        RequestDictionary[statesAllRequests.RequestDataType]()
        if(Request["OutputPdf"]==False):
            if(len(statesAllRequests.figs)>0):
                FigIndex=statesAllRequests.figsNames.index(statesAllRequests.RequestNameFormat1)
                statesAllRequests.figs.pop(FigIndex)
                statesAllRequests.figsNames.pop(FigIndex)
        if(Request["OutputExcel"]==False):
            del statesAllRequests.OutputSheets[statesAllRequests.RequestNameFormat1]
        _u_Reset.ResetRequestSpecificStates()
        print("Request"+str(i+1))
    print("r")
    _v_WriteFiles.WritePDfAndExcel()

def BaseReactions():
    BaseReactionFunction.BaseReactionFunction()

def JointReactions():
    SelectedPointsForCurrentRequest.GetSelectedPoints()
    SelectedFrames.GetSelectedFrames()
    SelectedAreasForCurrentRequest.GetSelectedAreas()
    JointReactionFunction.JointReactionFunction()
    PlotStructure.PlotStructure()
    PlotColumnsAndBraces.PlotColumnsAndBraces()
    PlotPointParameters.PlotPointParameters()

def DiaphragmForces():
    SelectedPointsForCurrentRequest.GetSelectedPoints()
    SelectedFrames.GetSelectedFrames()
    SelectedAreasForCurrentRequest.GetSelectedAreas()
    DiaphragmForcesFunction.GetDiaphragmForces()
    PlotStructure.PlotStructure()
    PlotColumnsAndBraces.PlotColumnsAndBraces()
    PlotVectorsAndPointParameters.PlotVectorsAndPoints()

def DiaphragmBraceFoces():
    SelectedPointsForCurrentRequest.GetSelectedPoints()
    SelectedFrames.GetSelectedFrames()
    SelectedAreasForCurrentRequest.GetSelectedAreas()
    DiaphragmBraceForcesFunction.GetDiaphragmBraceFoces()
    PlotStructure.PlotStructure()
    PlotColumnsAndBraces.PlotColumnsAndBraces()
    PlotVectorsAndPointParameters.PlotVectorsAndPoints()

def EndForces():
    SelectedPointsForCurrentRequest.GetSelectedPoints()
    SelectedFrames.GetSelectedFrames()
    SelectedAreasForCurrentRequest.GetSelectedAreas()
    EndForcesFunction.GetEndForcesSpreadsheet()
    PlotStructure.PlotStructure()
    PlotColumnsAndBraces.PlotColumnsAndBraces()
    PlotPointParameters.PlotPointParameters()

def FramingPlan():
    SelectedPointsForCurrentRequest.GetSelectedPoints()
    SelectedFrames.GetSelectedFrames()
    SelectedAreasForCurrentRequest.GetSelectedAreas()
    FramingPlanFunctions.GetFramingPlan()
    PlotStructure.PlotStructure()
    PlotColumnsAndBraces.PlotColumnsAndBraces()
    PlotText.PlotText()

def FramingModifiers():
    SelectedPointsForCurrentRequest.GetSelectedPoints()
    SelectedFrames.GetSelectedFrames()
    SelectedAreasForCurrentRequest.GetSelectedAreas()
    ModifierFunctions.GetModifiers()
    PlotStructure.PlotStructure()
    PlotColumnsAndBraces.PlotColumnsAndBraces()
    PlotText.PlotText()

def FramingReleases():
    SelectedPointsForCurrentRequest.GetSelectedPoints()
    SelectedFrames.GetSelectedFrames()
    SelectedAreasForCurrentRequest.GetSelectedAreas()
    ReleasesFunctions.GetReleases()
    PlotStructure.PlotStructure()
    PlotColumnsAndBraces.PlotColumnsAndBraces()
    PlotText.PlotText()

def JointDisplacements():
    SelectedPointsForCurrentRequest.GetSelectedPoints()
    SelectedFrames.GetSelectedFrames()
    SelectedAreasForCurrentRequest.GetSelectedAreas()
    JointDisplacementFunction.GetJointDisplacements()
    PlotStructure.PlotStructure()
    PlotColumnsAndBraces.PlotColumnsAndBraces()
    PlotPointParameters.PlotPointParameters()

def JointDrifts():
    SelectedPointsForCurrentRequest.GetSelectedPoints()
    SelectedFrames.GetSelectedFrames()
    SelectedAreasForCurrentRequest.GetSelectedAreas()
    JointDriftFunction.GetJointDrifts()
    PlotStructure.PlotStructure()
    PlotColumnsAndBraces.PlotColumnsAndBraces()
    PlotPointParameters.PlotPointParameters()

def LoadAssigns():
    SelectedPointsForCurrentRequest.GetSelectedPoints()
    SelectedFrames.GetSelectedFrames()
    SelectedAreasForCurrentRequest.GetSelectedAreas()
    AreaLoadAssignmentsUniform.GetAreaLoadAssignmentsUniform()
    statesAllRequests.PlotTable=[]
    FrameLoadAssignmentsDistributed.GetFrameLoadAssignmentsDistributed()
    PlotStructure.PlotStructure()
    PlotColumnsAndBraces.PlotColumnsAndBraces()
    PlotText.PlotText()

def MaxFrameForces():
    SelectedPointsForCurrentRequest.GetSelectedPoints()
    SelectedFrames.GetSelectedFrames()
    SelectedAreasForCurrentRequest.GetSelectedAreas()
    MaxFrameForcesFunction.GetMaxFrameForcesSpreadsheet()
    PlotStructure.PlotStructure()
    PlotColumnsAndBraces.PlotColumnsAndBraces()
    PlotPointParameters.PlotPointParameters()

def ModalProperties():
    ModalPropertiesFunction.GetModalPropertiesSpreadsheet()

def SteelFrameDesign360_16():
    SelectedPointsForCurrentRequest.GetSelectedPoints()
    SelectedFrames.GetSelectedFrames()
    SelectedAreasForCurrentRequest.GetSelectedAreas()
    SteelDesignFunctions.GetSteelDesign360_16()
    PlotStructure.PlotStructure()
    PlotColumnsAndBraces.PlotColumnsAndBraces()
    PlotText.PlotText()

def StoryForces():
    StoryForcesFunction.GetStoryForcesSpreadsheet()

RequestDictionary={
    "Base Reactions": BaseReactions,
    "Diaphragm Forces": DiaphragmForces,
    "Diaphragm Brace Forces": DiaphragmBraceFoces,
    "End Forces": EndForces,
    "Framing": FramingPlan,
    "Frame Releases": FramingReleases,
    "Frame Modifiers": FramingModifiers,
    "Joint Displacements": JointDisplacements,
    "Joint Drifts": JointDrifts,
    "Joint Reactions": JointReactions,
    "Load Assigns": LoadAssigns,
    "Modal Properties": ModalProperties,
    "Max Frame Forces": MaxFrameForces,
    "Steel Design 360-16": SteelFrameDesign360_16,
    "Story Forces": StoryForces,
}