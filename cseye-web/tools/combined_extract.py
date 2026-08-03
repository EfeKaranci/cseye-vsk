"""
Attach to the already-open ETABS instance and extract BOTH geometry and
available forces/reactions in one pass. Read-only, no save.
Writes geom_240g.json and forces_240g.json.
"""
import sys, json, os, time
from collections import Counter, defaultdict
SC=r"C:\Users\ekaranci\AppData\Local\Temp\claude\c--Analysis-WC2026\da951d2a-a94b-4be2-a4a4-4acf28fa31ac\scratchpad"
log=lambda m:print(m,flush=True); R=lambda v:round(float(v),4); R3=lambda v:round(float(v),3)
WANT_COMBOS=["LRFD_Env_New","LRFD_Env_Existing","ASD_Env_New","ASD_Env_Existing",
             "LRFD_1.2D_Exisitng+1.6L_Existing","ASD_1.0D_Exisitng+1.0L_Existing","1.0D","Siesmic_env"]

def get_table(sm,name):
    try:
        t=sm.DatabaseTables.GetTableForDisplayArray(name,"","",21,"")
        ncol=len(t[2]);headers=list(t[2]);flat=list(t[4])
        rows=[flat[i:i+ncol] for i in range(0,len(flat),ncol)]
        return [dict(zip(headers,r)) for r in rows]
    except Exception as e:
        log(f"  (table {name} n/a: {e})");return []

def main():
    import comtypes.client
    helper=comtypes.client.CreateObject("ETABSv1.Helper")
    helper=helper.QueryInterface(comtypes.gen.ETABSv1.cHelper)
    obj=helper.GetObject("CSI.ETABS.API.ETABSObject")
    if obj is None: log("ERROR: no ETABS instance."); sys.exit(2)
    sm=obj.SapModel; sm.SetPresentUnits(4)
    log(f"Attached: {sm.GetModelFilename()}  locked={sm.GetModelIsLocked()}")

    # ---------- geometry ----------
    st=sm.Story.GetStories_2()
    stories=[{"name":n.strip(),"elev":R(e)} for n,e in zip(st[2],st[3])]
    ptnames=sm.PointObj.GetNameList()[1]
    points={nm:[R(c[0]),R(c[1]),R(c[2])] for nm in ptnames
            for c in [sm.PointObj.GetCoordCartesian(nm,0.,0.,0.)]}
    ORIENT={1:"column",2:"beam",3:"brace",4:"null",5:"other"}
    frnames=sm.FrameObj.GetNameList()[1]; frames=[]; tally=Counter()
    t0=time.time()
    for k,nm in enumerate(frnames):
        try:o=sm.FrameObj.GetDesignOrientation(nm)[0]
        except Exception:o=-1
        typ=ORIENT.get(o,"unknown")
        pts=sm.FrameObj.GetPoints(nm,"","")
        lbl=sm.FrameObj.GetLabelFromName(nm)
        sec=sm.FrameObj.GetSection(nm)[0]
        frames.append({"name":nm,"label":lbl[0],"story":lbl[1].strip(),"type":typ,"i":pts[0],"j":pts[1],"sec":sec})
        tally[typ]+=1
    log(f"geom: {len(stories)} stories, {len(points)} pts, {len(frames)} frames {dict(tally)} in {time.time()-t0:.0f}s")
    grid_rows=get_table(sm,"Grid Definitions - Grid Lines")
    xs=[p[0] for p in points.values()];ys=[p[1] for p in points.values()]
    extents={"xmin":R(min(xs)),"xmax":R(max(xs)),"ymin":R(min(ys)),"ymax":R(max(ys))}
    geom={"model":sm.GetModelFilename(),"etabs_version":sm.GetVersion()[0],"units":"kip, ft",
          "has_results":sm.GetModelIsLocked(),"extents":extents,"stories":stories,
          "points":points,"frames":frames,"grids_raw":grid_rows}
    json.dump(geom,open(os.path.join(SC,"geom_240g.json"),"w"),separators=(",",":"))
    log("wrote geom_240g.json")

    # ---------- forces (if analyzed) ----------
    if not sm.GetModelIsLocked():
        log("model unlocked -> skipping forces"); return
    cst=sm.Analyze.GetCaseStatus(); finished=[n for n,s in zip(cst[1],cst[2]) if s==4]
    combos=set(sm.RespCombo.GetNameList()[1])
    log(f"finished cases: {finished}")
    setup=sm.Results.Setup; setup.DeselectAllCasesAndCombosForOutput()
    for c in finished: setup.SetCaseSelectedForOutput(c)
    for c in WANT_COMBOS:
        if c in combos: setup.SetComboSelectedForOutput(c)
    cols=[f["name"] for f in frames if f["type"]=="column"]
    col_forces={}; seen=set(); t0=time.time()
    zmap={nm:points[nm][2] for nm in points}
    for k,nm in enumerate(cols):
        f=next(x for x in frames if x["name"]==nm)
        zi,zj=zmap.get(f["i"],0),zmap.get(f["j"],0)
        ff=sm.Results.FrameForce(nm,0); n=ff[0]
        if not n: continue
        sta=ff[2]; base=min(sta) if zi<=zj else max(sta)
        per=defaultdict(lambda:{"Pmin":1e30,"Pmax":-1e30,"V2":0,"V3":0,"M2":0,"M3":0})
        for r in range(n):
            if abs(sta[r]-base)>1e-4: continue
            cse=ff[5][r];P=ff[8][r];seen.add(cse);d=per[cse]
            if P<d["Pmin"]:d["Pmin"]=P
            if P>d["Pmax"]:d["Pmax"]=P;d["V2"]=ff[9][r];d["V3"]=ff[10][r];d["M2"]=ff[12][r];d["M3"]=ff[13][r]
        col_forces[nm]={c:{kk:R3(vv) for kk,vv in d.items()} for c,d in per.items()}
    log(f"force sets: {sorted(seen)} in {time.time()-t0:.0f}s")
    jr=sm.Results.JointReact("All",2); n=jr[0]; acc=defaultdict(dict)
    for i in range(n):
        acc[jr[1][i]][jr[3][i]]={"Fx":R3(jr[6][i]),"Fy":R3(jr[7][i]),"Fz":R3(jr[8][i]),
                                 "Mx":R3(jr[9][i]),"My":R3(jr[10][i]),"Mz":R3(jr[11][i])}
    reactions={}
    for j,cs in acc.items():
        if max((abs(v["Fz"]) for v in cs.values()),default=0)>0.5 or max((max(abs(v["Fx"]),abs(v["Fy"])) for v in cs.values()),default=0)>0.5:
            c=sm.PointObj.GetCoordCartesian(j,0.,0.,0.)
            reactions[j]={"x":R3(c[0]),"y":R3(c[1]),"z":R3(c[2]),"cases":cs}
    forces={"model":sm.GetModelFilename(),"units":"kip, ft","result_sets":sorted(seen),
            "col_forces":col_forces,"reactions":reactions}
    json.dump(forces,open(os.path.join(SC,"forces_240g.json"),"w"),separators=(",",":"))
    log(f"wrote forces_240g.json ({len(reactions)} supports, {len(col_forces)} cols)")

if __name__=="__main__":
    try:main()
    except Exception:
        import traceback;traceback.print_exc();sys.exit(1)
