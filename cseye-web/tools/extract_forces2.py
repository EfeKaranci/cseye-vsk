"""
Forces + reactions incl. LOAD COMBINATIONS, reusing existing geom json for the
column list. Attaches to the open ETABS. Read-only. Writes forces_240g.json.
"""
import sys, json, os, time
from collections import defaultdict
SC=r"C:\Users\ekaranci\AppData\Local\Temp\claude\c--Analysis-WC2026\da951d2a-a94b-4be2-a4a4-4acf28fa31ac\scratchpad"
log=lambda m:print(m,flush=True); R3=lambda v:round(float(v),3)

def main():
    import comtypes.client
    geom=json.load(open(os.path.join(SC,"geom_240g.json")))
    pts={k:v for k,v in geom["points"].items()}
    cols=[f for f in geom["frames"] if f["type"]=="column"]
    helper=comtypes.client.CreateObject("ETABSv1.Helper")
    helper=helper.QueryInterface(comtypes.gen.ETABSv1.cHelper)
    obj=helper.GetObject("CSI.ETABS.API.ETABSObject")
    if obj is None: log("ERROR: no ETABS instance."); sys.exit(2)
    sm=obj.SapModel; sm.SetPresentUnits(4)
    log(f"Attached: {sm.GetModelFilename()} locked={sm.GetModelIsLocked()}")

    cst=sm.Analyze.GetCaseStatus(); finished=[n for n,s in zip(cst[1],cst[2]) if s==4]
    case_names=set(sm.LoadCases.GetNameList()[1])
    combo_names=list(sm.RespCombo.GetNameList()[1])
    log(f"finished cases: {len(finished)} | combos defined: {len(combo_names)}")

    setup=sm.Results.Setup; setup.DeselectAllCasesAndCombosForOutput()
    for c in finished: setup.SetCaseSelectedForOutput(c)
    for c in combo_names: setup.SetComboSelectedForOutput(c)  # combos w/o results simply return nothing

    col_forces={}; seen=set(); t0=time.time()
    for k,f in enumerate(cols):
        nm=f["name"]; zi=pts.get(f["i"],[0,0,0])[2]; zj=pts.get(f["j"],[0,0,0])[2]
        ff=sm.Results.FrameForce(nm,0); n=ff[0]
        if not n: continue
        sta=ff[2]; base=min(sta) if zi<=zj else max(sta)
        per=defaultdict(lambda:{"Pmin":1e30,"Pmax":-1e30,"V2":0,"V3":0,"M2":0,"M3":0})
        for r in range(n):
            if abs(sta[r]-base)>1e-4: continue
            cse=ff[5][r]; P=ff[8][r]; seen.add(cse); d=per[cse]
            if P<d["Pmin"]: d["Pmin"]=P
            if P>d["Pmax"]: d["Pmax"]=P; d["V2"]=ff[9][r]; d["V3"]=ff[10][r]; d["M2"]=ff[12][r]; d["M3"]=ff[13][r]
        col_forces[nm]={c:{kk:R3(vv) for kk,vv in d.items()} for c,d in per.items()}
        if k and k%700==0: log(f"  {k}/{len(cols)} ({time.time()-t0:.0f}s)")
    log(f"result sets w/ forces: {len(seen)} in {time.time()-t0:.0f}s")

    # capture Fz min/max across steps (envelope combos return Max & Min) + governing (max |Fz|) components
    jr=sm.Results.JointReact("All",2); n=jr[0]
    acc=defaultdict(lambda:defaultdict(lambda:{"fzmin":1e30,"fzmax":-1e30,"gabs":-1.0,"gov":None}))
    for i in range(n):
        d=acc[jr[1][i]][jr[3][i]]; Fz=jr[8][i]
        if Fz<d["fzmin"]: d["fzmin"]=Fz
        if Fz>d["fzmax"]: d["fzmax"]=Fz
        a=abs(Fz)
        if a>d["gabs"]:
            d["gabs"]=a; d["gov"]={"Fx":jr[6][i],"Fy":jr[7][i],"Fz":Fz,"Mx":jr[9][i],"My":jr[10][i],"Mz":jr[11][i]}
    reactions={}
    for j,cs in acc.items():
        built={}
        for rs,d in cs.items():
            g=d["gov"] or {"Fx":0,"Fy":0,"Fz":0,"Mx":0,"My":0,"Mz":0}
            built[rs]={"Fx":R3(g["Fx"]),"Fy":R3(g["Fy"]),"Fz":R3(g["Fz"]),
                       "Mx":R3(g["Mx"]),"My":R3(g["My"]),"Mz":R3(g["Mz"]),
                       "Fzmin":R3(d["fzmin"]),"Fzmax":R3(d["fzmax"])}
        if max((abs(v["Fzmax"]) for v in built.values()),default=0)>0.5 or \
           max((abs(v["Fzmin"]) for v in built.values()),default=0)>0.5 or \
           max((max(abs(v["Fx"]),abs(v["Fy"])) for v in built.values()),default=0)>0.5:
            c=sm.PointObj.GetCoordCartesian(j,0.,0.,0.)
            reactions[j]={"x":R3(c[0]),"y":R3(c[1]),"z":R3(c[2]),"cases":built}

    kinds={nm:("combo" if nm in [x for x in combo_names] else "case") for nm in seen}
    order=sorted(seen, key=lambda n:(kinds[n]!="case", n))  # cases first, then combos
    forces={"model":sm.GetModelFilename(),"units":"kip, ft","result_sets":order,
            "result_kinds":kinds,"col_forces":col_forces,"reactions":reactions}
    json.dump(forces,open(os.path.join(SC,"forces_240g.json"),"w"),separators=(",",":"))
    sz=os.path.getsize(os.path.join(SC,"forces_240g.json"))/1e6
    ncase=sum(1 for v in kinds.values() if v=="case"); ncombo=sum(1 for v in kinds.values() if v=="combo")
    log(f"wrote forces_240g.json {sz:.2f} MB | {ncase} cases + {ncombo} combos | {len(reactions)} supports")
    log("cases: "+", ".join(n for n in order if kinds[n]=="case"))
    log("combos: "+", ".join(n for n in order if kinds[n]=="combo"))

if __name__=="__main__":
    try: main()
    except Exception:
        import traceback; traceback.print_exc(); sys.exit(1)
