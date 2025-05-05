import database.tableSetup as tableSetup
import states.statesAllRequests as statesAllRequests
def ConvertListOfListsToListOfDictionaries(ListOfLists):
    Header=ListOfLists[0]
    NewListOfDictionaries=[]
    for row in ListOfLists[1:]:
        NewRow={}
        for index,element in enumerate(row):
            Key=Header[index]
            if(Key!=None):NewRow[Key]=element
        if(NewRow!={}):NewListOfDictionaries.append(NewRow)
    return NewListOfDictionaries

def ConvertListOfListstoDictionaries(ListOfLists):
    return ListOfLists

def resetDefaultRow():
    statesAllRequests.defaultRow={tableSetup.RequestKeys[0]:False,
            tableSetup.RequestKeys[1]:"Run",
            tableSetup.RequestKeys[2]:"Framing", tableSetup.RequestKeys[3]:"Sections",
            tableSetup.RequestKeys[4]:"", tableSetup.RequestKeys[5]:"",
            tableSetup.RequestKeys[6]:"", tableSetup.RequestKeys[7]:"",tableSetup.RequestKeys[8]:[""], 
            tableSetup.RequestKeys[9]:"",
            tableSetup.RequestKeys[10]:1, tableSetup.RequestKeys[11]:1, tableSetup.RequestKeys[12]:1,
            tableSetup.RequestKeys[13]:True,tableSetup.RequestKeys[14]:True}