import pandas as pd
import states.statesAllRequests as statesAllRequests
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.colors as mcolors
import database.tableSetup as tableSetup
import io
from matplotlib.backends.backend_pdf import PdfPages
from PyPDF2 import PdfReader, PdfWriter
def build_tables():
    tables = {}
    for sheet_name, dicts in statesAllRequests.OutputSheets.items():
        if(len(dicts)>0):
            rows = ConvertListOfDictionariesToListOfLists(dicts)
            # Prepend the units row
            units_row = [f"Units = {statesAllRequests.SelectedUnits}"]
            # If rows isn't empty, insert at top; otherwise make sure there's at least header
            if len(rows)>0:
                rows.insert(0, units_row)
            else:
                rows = [units_row]
            tables[sheet_name] = rows
    return tables

def ConvertListOfDictionariesToListOfLists(ListOfDicts):
    header = list(ListOfDicts[0].keys())
    rows = [header]
    for d in ListOfDicts:
        row = [d[key] for key in header]
        rows.append(row)
    #rows = [headercleaned] + rows
    return rows

def WriteDictionaryWithTables(tables, path):
    if tables==None:
        return
    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        wrote_any = False
        for sheet_name, data in tables.items():
            if not data:
                continue
            data.insert(0,[sheet_name])
            df = pd.DataFrame(data)
            df.to_excel(
                writer,
                sheet_name=sheet_name[:31] or "Sheet1",
                index=False,
                header=False
            )
            wrote_any = True
        if not wrote_any:
            pd.DataFrame().to_excel(writer, sheet_name="Sheet1")

def WritePdfPlot(figs, path):
    # 1) Render all the Matplotlib figures into an in-memory PDF
    buffer = io.BytesIO()
    with PdfPages(buffer) as pdf:
        for fig in figs:
            pdf.savefig(fig, bbox_inches="tight")
    buffer.seek(0)

    # 2) Read that PDF back in
    reader = PdfReader(buffer)
    writer = PdfWriter()

    # 3) Copy pages into the writer, adding a bookmark for each
    for i, page in enumerate(reader.pages):
        writer.add_page(page)
        # Use the corresponding name from your list
        title = statesAllRequests.figsNames[i]
        writer.add_outline_item(title, i)  # bookmark at top‐level

    # 4) Write out the final, bookmarked PDF
    with open(path, "wb") as f:
        writer.write(f)

def WriteTable(Table,Path):
    df = pd.DataFrame(Table)
    df.to_excel(Path, index=False, header=False)

def GetDataIndices(Header,Value):
    try:
        Index = Header.index(Value)
    except ValueError:
        Index = None
    return Index

def GetJoint(JointName):
    return next((x for x in statesAllRequests.SelectedPointsForCurrentRequest if x["UniqueName"] == JointName), None)

def CheckForInteger(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

def CheckforPositivefloat(value):
    try:
        f = float(value)
        return f > 0
    except ValueError:
        return False
def GetStressColor(stress_ratio):
    colors = ["violet", "indigo", "blue", "green", "yellow", "orange", "red"]
    stress_cmap = mcolors.LinearSegmentedColormap.from_list("stress_cmap", colors)
    color = stress_cmap(stress_ratio)
    return color

def DeConstructFrame(Frame):
    UniqueName, PtIName, PtJName,Story,FrameType = Frame
    return UniqueName, PtIName, PtJName,Story,FrameType

def DeConstructFloor(Floor):
    UniqueName, PtNames = Floor[0],Floor[1]
    return UniqueName, PtNames

def GetPointByName(PtName):
    return next((x for x in statesAllRequests.SelectedPointsForCurrentRequest if x['UniqueName'] == PtName), None)

def GetViewCoordinates(PtPlanesData):
    return next((PtPlaneData["Coords"] for PtPlaneData in PtPlanesData if
                 PtPlaneData['ViewType'] == statesAllRequests.RequestViewType and
                 PtPlaneData['ViewLabels'] == statesAllRequests.RequestViewLabel and
                 PtPlaneData['GridSystem'] == statesAllRequests.RequestGridSystem), None)

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

def resetDefaultRow():
    statesAllRequests.defaultRow={tableSetup.RequestKeys[0]:False,
            tableSetup.RequestKeys[1]:"Run",
            tableSetup.RequestKeys[2]:"Framing", tableSetup.RequestKeys[3]:"Sections",
            tableSetup.RequestKeys[4]:"", tableSetup.RequestKeys[5]:"",
            tableSetup.RequestKeys[6]:"", tableSetup.RequestKeys[7]:"",tableSetup.RequestKeys[8]:[""], 
            tableSetup.RequestKeys[9]:"",
            tableSetup.RequestKeys[10]:1, tableSetup.RequestKeys[11]:1, tableSetup.RequestKeys[12]:1,
            tableSetup.RequestKeys[13]:True,tableSetup.RequestKeys[14]:True}