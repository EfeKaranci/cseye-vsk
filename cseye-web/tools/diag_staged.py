"""Attach to a running ETABS and inspect how a nonlinear staged-construction case
(default 'CSA LT') reports its steps, plus the stage names/comments. Run this with
the model open + the staged case analyzed, to finalize per-stage step labels."""
import sys
CASE = sys.argv[1] if len(sys.argv) > 1 else "CSA LT"
log = lambda m: print(m, flush=True)

def main():
    import comtypes.client
    helper = comtypes.client.CreateObject("ETABSv1.Helper")
    helper = helper.QueryInterface(comtypes.gen.ETABSv1.cHelper)
    obj = helper.GetObject("CSI.ETABS.API.ETABSObject")
    if obj is None:
        log("No running ETABS."); return
    sm = obj.SapModel; sm.SetPresentUnits(4)
    log(f"Model: {sm.GetModelFilename()}  locked={sm.GetModelIsLocked()}")

    # stage definitions (names / comments / output flags)
    try:
        sd = sm.LoadCases.StaticNonlinearStaged.GetStageData_2(CASE)
        log(f"GetStageData_2 raw: {sd}")
    except Exception as e:
        log(f"GetStageData_2 failed: {e}")

    setup = sm.Results.Setup
    setup.DeselectAllCasesAndCombosForOutput()
    setup.SetCaseSelectedForOutput(CASE)
    for opt in (("SetOptionNLStatic", 2), ("SetOptionMultiStepStatic", 2)):
        try: getattr(setup, opt[0])(opt[1])
        except Exception: pass

    col = next((nm for nm in sm.FrameObj.GetNameList()[1] if sm.FrameObj.GetDesignOrientation(nm)[0] == 1), None)
    ff = sm.Results.FrameForce(col, 0); n = ff[0]
    steps = []
    for i in range(n):
        s = (str(ff[6][i]).strip(), ff[7][i])
        if s not in steps: steps.append(s)
    log(f"[{CASE}] FrameForce col {col}: rows={n}  distinct (StepType,StepNum): {steps[:40]}")

    jr = sm.Results.JointReact("All", 2)
    js = []
    for i in range(jr[0]):
        s = (str(jr[4][i]).strip(), jr[5][i])
        if s not in js: js.append(s)
    log(f"[{CASE}] JointReact: rows={jr[0]}  distinct steps: {js[:40]}")

if __name__ == "__main__":
    try: main()
    except Exception:
        import traceback; traceback.print_exc()
