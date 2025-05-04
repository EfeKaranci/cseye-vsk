import database.tableSetup as tableSetup

sapModel=None
modelPath=None

StoryDefinitions=[]
TowerAndBaseDefinitions=[]
GridDefinitions=[]
GridSystems=[]
LoadCombinationDefinitions=[]
GroupDefinitions=[]

defaultRow={tableSetup.RequestKeys[0]:False,
            tableSetup.RequestKeys[1]:"Run",
            tableSetup.RequestKeys[2]:"Framing", tableSetup.RequestKeys[3]:"Sections",
            tableSetup.RequestKeys[4]:"", tableSetup.RequestKeys[5]:"",
            tableSetup.RequestKeys[6]:"", tableSetup.RequestKeys[7]:"",tableSetup.RequestKeys[8]:[""], 
            tableSetup.RequestKeys[9]:"",
            tableSetup.RequestKeys[10]:1, tableSetup.RequestKeys[11]:1, tableSetup.RequestKeys[12]:1,
            tableSetup.RequestKeys[13]:True,tableSetup.RequestKeys[14]:True}

Requests=[]