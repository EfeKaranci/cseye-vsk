import states.statesAllRequests as statesAllRequests
import database.tableSetup as tableSetup
import hooks.csiHooks as csiHooks
import states.statesUI as statesUI
import _2_initializeModules as _2_initializeModules
def getModelData():
    statesAllRequests.StoryDefinitions=csiHooks.GetAndProcessCSITable('Story Definitions',"")
    statesAllRequests.TowerAndBaseDefinitions=csiHooks.GetAndProcessCSITable('Tower and Base Story Definitions',"")
    statesAllRequests.GridDefinitions=csiHooks.GetAndProcessCSITable("Grid Definitions - Grid Lines","")
    statesAllRequests.GridSystems=csiHooks.GetAndProcessCSITable("Grid Definitions - General","")
    statesAllRequests.LoadCombinationDefinitions=csiHooks.GetAndProcessCSITable('Load Combination Definitions',"")
    statesAllRequests.LoadCaseDefinitions=csiHooks.GetAndProcessCSITable('Load Case Definitions - Summary',"")
    statesAllRequests.GroupDefinitions=csiHooks.GetAndProcessCSITable('Group Definitions',"")

    tableSetup.StoryNames=[x["Story"] for x in statesAllRequests.StoryDefinitions]+[x["BSName"] for x in statesAllRequests.TowerAndBaseDefinitions]
    tableSetup.GridSystemNames=[x["Name"] for x in statesAllRequests.GridSystems]
    tableSetup.GridSystemNames=[{x:[y["ID"] for y in statesAllRequests.GridDefinitions if y["Name"]==x]} for x in tableSetup.GridSystemNames]
    tableSetup.GridSystemNames=tableSetup.GridSystemNames
    tableSetup.LoadCombinationNames=list(set([x["Name"] for x in statesAllRequests.LoadCombinationDefinitions]))
    tableSetup.LoadCombinationNames=tableSetup.LoadCombinationNames+[x["Name"] for x in statesAllRequests.LoadCaseDefinitions]
    tableSetup.GroupNames=[""]+[x["Name"] for x in statesAllRequests.GroupDefinitions]
    pass

    if len(tableSetup.StoryNames)>0 or len(tableSetup.GridSystemNames)>0:
        if len(tableSetup.StoryNames)>0:
            statesAllRequests.defaultRow["ViewType"]="Story"
            statesAllRequests.defaultRow["ViewLabels"]=[tableSetup.StoryNames[-1]]
        else:
            statesAllRequests.defaultRow["ViewType"]="Elevation"
            statesAllRequests.defaultRow["GridSystem"]=[tableSetup.GridSystemNames[0]["GridSystem"]]
            if len(statesAllRequests.defaultRow[0]["Gridlines"])>0:
                statesAllRequests.defaultRow["ViewLabels"]=[tableSetup.GridSystemNames[0]["Gridlines"][0]]
    
    moduleScreen=_2_initializeModules.ModulesScreen()
    statesUI.widget.addWidget(moduleScreen)
    statesUI.widget.setCurrentIndex(statesUI.widget.currentIndex()+1)