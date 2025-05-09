import states.statesAllRequests as statesAllRequests
import Hooks.BasicHooks as BasicHooks
import Hooks.AnalysisResultsHooks as AnalysisResultsHooks

def GetModalPropertiesSpreadsheet():
    if("Modal Periods And Frequencies" in statesAllRequests.SelectedCSITables):
        print("Modal Periods And Frequencies")
    OriginalSheetName=statesAllRequests.RequestNameFormat1
    FirstDelimiterIndex=OriginalSheetName.find('_')
    ModalPeriodsSheet=OriginalSheetName[:FirstDelimiterIndex] + "a" + "_" + "Modal Periods and Frequencies"
    ModalDirectionFactorsSheet=OriginalSheetName[:FirstDelimiterIndex] + "b" + "_" + "Modal Direction Factors"
    ModalLoadParticipationRatiosSheet=OriginalSheetName[:FirstDelimiterIndex] + "c" + "_" + "Modal Load Participation Ratios"
    ModalParticipatingMassRatiosSheet=OriginalSheetName[:FirstDelimiterIndex] + "d" + "_" + "Modal Participating Mass Ratios"
    ModalParticipationFactorsSheet=OriginalSheetName[:FirstDelimiterIndex] + "e" + "_" + "Modal Participation Factors"
    ModalCaseDefinitionsEigenSheet=OriginalSheetName[:FirstDelimiterIndex] + "f" + "_" + "Modal Case Definitions - Eigen"
    statesAllRequests.OutputSheets[ModalPeriodsSheet] = statesAllRequests.SelectedCSITables["Modal Periods And Frequencies"]
    statesAllRequests.OutputSheets[ModalDirectionFactorsSheet] = statesAllRequests.SelectedCSITables["Modal Direction Factors"]
    statesAllRequests.OutputSheets[ModalLoadParticipationRatiosSheet] = statesAllRequests.SelectedCSITables["Modal Load Participation Ratios"]
    statesAllRequests.OutputSheets[ModalParticipatingMassRatiosSheet] = statesAllRequests.SelectedCSITables["Modal Participating Mass Ratios"]
    statesAllRequests.OutputSheets[ModalParticipationFactorsSheet] = statesAllRequests.SelectedCSITables["Modal Participation Factors"]
    statesAllRequests.OutputSheets[ModalCaseDefinitionsEigenSheet] = statesAllRequests.SelectedCSITables["Modal Case Definitions - Eigen"]

