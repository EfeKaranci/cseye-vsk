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