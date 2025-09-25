import states.statesAllRequests as statesAllRequests
import hooks.basicHooks as BasicHooks
import _u_Reset as _u_Reset
import states.statesUI as statesUI

def WritePDfAndExcel():
    print("1")
    statesUI.counter+=1
    statesUI.update_status()
    print("2")
    OutputExcelPath= (statesAllRequests.OutputFolder.replace("\"", "")) + "\\" + statesAllRequests.OutputName + ".xlsx"
    OutputPdfPath= (statesAllRequests.OutputFolder.replace("\"", "")) + "\\" + statesAllRequests.OutputName + ".pdf"
    print("3")
    #Output
    tables = BasicHooks.build_tables()
    print("4")
    BasicHooks.WriteDictionaryWithTables(tables,OutputExcelPath)
    print("5")
    if(len(statesAllRequests.figs)>0):BasicHooks.WritePdfPlot(statesAllRequests.figs, OutputPdfPath)
    print("v")
    _u_Reset.ResetGeneralStates()