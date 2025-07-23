
mainHeaders = ["","Request","Load (If Applicable)","View","Output For Group Only?","Formatting","Output Options"]

mainHeaderspans = [1,3, 2, 3, 1, 3,2]  # Total = 12 columns.
subHeaders = [  "","Run?",
                "Data Type", "Data",
                "Load Case/Combination", "Load Step",
                "View Type", "Grid System (If Applicable)","View Labels", 
                "Group Name(s)",
                "No. Of Decimal Places", "Text Scale", "Marker Scale",
                "Output Pdf?","Output Excel?"]

RequestKeys=["Selected","Run","DataType","Data","LoadCase","LoadStep","ViewType","GridSystem","ViewLabels","GroupName","DecimalPlaces","TextScale","MarkerScale","OutputPdf","OutputExcel"]

cellWidgets={RequestKeys[0]:"checkbox",
            RequestKeys[1]:"combobox",
            RequestKeys[2]:"combobox", RequestKeys[3]:"combobox",
            RequestKeys[4]:"combobox", RequestKeys[5]:"combobox",
            RequestKeys[6]:"combobox", RequestKeys[7]:"combobox",RequestKeys[8]:"comboboxMultiple", 
            RequestKeys[9]:"combobox",
            RequestKeys[10]:"spinbox", RequestKeys[11]:"spinbox", RequestKeys[12]:"spinbox",
            RequestKeys[13]:"checkbox", RequestKeys[14]:"checkbox"}

subHeaderspans = [1,1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

runOptions = ["Run", "Do not run"]

dataOptions = {
            "Base Reactions": ["Base Reactions"],#Excel Only
            #"Column Design Takedown": ["Steel Design 360-16"],
            #"Column Load Takedown": ["P", "V2", "V3", "T", "M2", "M3"],
            "Composite Beam Design": ["Design","Percentage Composite","Design Reactions","Max Moment","Design Ratios"],
            "Diaphragm Forces": ["Applied Force", "Reactive Force", "Diaphragm Force"],
            "Diaphragm Brace Forces": ["Diaphragm Brace Forces"],
            "End Forces": ["P", "V2", "V3", "T", "M2", "M3"],
            #"End Forces-Rounded": ["P", "V2", "V3", "T", "M2", "M3"],
            "Framing": ["Frames","Areas"],
            "Frame Releases": ["P", "V2", "V3", "T", "M2", "M3","All"],
            "Frame Modifiers": ["Area", "As2", "As3", "J", "I2", "I3", "Mass", "Weight"],
            "Joint Displacements": ["Ux", "Uy", "Uz", "Rx", "Ry", "Rz", "All", ""],
            "Joint Drifts": ["X", "Y"],
            "Joint Reactions": ["FX", "FY", "FZ", "MX", "MY", "MZ"],
            "Max Frame Forces": ["P(Abs)", "P(Comp)", "P(Tens)", "V2(Abs)", "V3(Abs)", "T(Abs)", "M2(Abs)", "M3(Abs)"],
            "Modal Properties": ["Modal Properties"],#Excel Only
            #"Restraints": ["All"],
            #"Load Assigns": ["Load Assigns"],
            "Steel Design 360-16": ["DCRs", "Design Combination", "PMM Breakdown"],
            #"Story Drift": ["X", "Y"],
            "Story Forces": ["Story Forces"], #Excel Only
            #"Tributary Areas": ["Beams", "Columns"],
            #"Uniform Load Sets": ["Uniform Load Sets"]
        }

LoadCombinationNames=[]

viewTypeOptions = ["Story", "Elevation"]

GridSystemNames=[]

StoryNames=[]

LoadSteps=["","max", "min"]+[str(i) for i in range(1,100)]

GroupNames=[]
# Dictionary to store help text for each subheader
helpTexts = {
    "Run?": "PLACEHOLDER: Help text for Run?",
    "Data Type": "PLACEHOLDER: Help text for Data Type",
    "Data": "PLACEHOLDER: Help text for Data",
    "Load Case/Combination": "PLACEHOLDER: Help text for Load Case/Combination",
    "Load Step": "PLACEHOLDER: Help text for Load Step",
    "View Type": "PLACEHOLDER: Help text for View Type",
    "Grid System (If Applicable)": "PLACEHOLDER: Help text for Grid System",
    "View Labels": "PLACEHOLDER: Help text for View Labels",
    "Group Name(s)": "PLACEHOLDER: Help text for Group Name(s)",
    "No. Of Decimal Places": "PLACEHOLDER: Help text for Decimal Places",
    "Text Scale": "PLACEHOLDER: Help text for Text Scale",
    "Marker Scale": "PLACEHOLDER: Help text for Marker Scale",
    "Output Pdf?": "PLACEHOLDER: Help text for Output Pdf?",
    "Output Excel?": "PLACEHOLDER: Help text for Output Excel?"
}

DataThatDoNotRequireRunModel = ["Framing","Frame Releases","Frame Modifiers","Restraints","Load Assigns"]

DataThatRequireSteelDesign = ["Steel Design 360-16"]

DataWithNoText = ["Base Reactions","Modal Properties","Story Forces"]

DataWithNoMarkers = ["Base Reactions","Modal Properties","Story Forces","Composite Beam Design","Framing","Frame Releases","Frame Modifiers","Restraints","Load Assigns","Steel Design 360-16"]

DataWithNoLoads = ["Modal Properties","Composite Beam Design","Framing","Frame Releases","Frame Modifiers","Restraints","Steel Design 360-16"]

DatawithNoDecimalPlaces = ["Base Reactions","Modal Properties","Story Forces","Composite Beam Design","Framing","Frame Releases","Frame Modifiers","Restraints","Steel Design 360-16"]

DataForStoryViewOnly = ["Base Reactions","Modal Properties","Story Forces","Column Design Takedown","Diaphragm Forces","Diaphragm Brace Forces","Story Drift","Story Forces"]

DataWithNoExcel = ["Framing"]

DataWithExcelOnly = ["Base Reactions","Modal Properties","Story Forces"]

DataWithNoPdf = ["Base Reactions","Modal Properties","Story Forces"]
