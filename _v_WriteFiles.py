import states.statesAllRequests as statesAllRequests
import Hooks.BasicHooks as BasicHooks
import _u_Reset as _u_Reset
def WritePDfAndExcel():
    OutputExcelPath= (statesAllRequests.OutputFolder.replace("\"", "")) + "\\" + statesAllRequests.OutputName + ".xlsx"
    OutputPdfPath= (statesAllRequests.OutputFolder.replace("\"", "")) + "\\" + statesAllRequests.OutputName + ".pdf"
    #Output
    tables = BasicHooks.build_tables()
    BasicHooks.WriteDictionaryWithTables(tables,OutputExcelPath)
    if(len(statesAllRequests.figs)>0):BasicHooks.WritePdfPlot(statesAllRequests.figs, OutputPdfPath)
    print("v")
    _u_Reset.ResetGeneralStates()