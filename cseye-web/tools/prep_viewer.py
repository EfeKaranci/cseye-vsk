"""Inject 240G geometry (+ derived grid segments) and forces into the viewer template."""
import json, os
SC=r"C:\Users\ekaranci\AppData\Local\Temp\claude\c--Analysis-WC2026\da951d2a-a94b-4be2-a4a4-4acf28fa31ac\scratchpad"
geom=json.load(open(os.path.join(SC,"geom_240g.json")))
e=geom["extents"]
def num(v):
    try:return float(v)
    except:return None
grid_lines=[]
for g in geom["grids_raw"]:
    lt=g.get("LineType","");vis=(g.get("Visible")=="Yes");gid=str(g.get("ID","")).strip()
    if lt.startswith("X"):
        o=num(g.get("Ordinate"))
        if o is None:continue
        grid_lines.append({"id":gid,"dir":"X","x1":o,"y1":e["ymin"],"x2":o,"y2":e["ymax"],"visible":vis})
    elif lt.startswith("Y"):
        o=num(g.get("Ordinate"))
        if o is None:continue
        grid_lines.append({"id":gid,"dir":"Y","x1":e["xmin"],"y1":o,"x2":e["xmax"],"y2":o,"visible":vis})
    else:
        x1,y1,x2,y2=num(g.get("X1")),num(g.get("Y1")),num(g.get("X2")),num(g.get("Y2"))
        if None in (x1,y1,x2,y2):continue
        grid_lines.append({"id":gid,"dir":"G","x1":x1,"y1":y1,"x2":x2,"y2":y2,"visible":vis})
out={"model":geom["model"],"etabs_version":geom["etabs_version"],"units":geom["units"],
     "has_results":geom.get("has_results",False),"extents":e,"stories":geom["stories"],
     "points":geom["points"],"frames":geom["frames"],"grid_lines":grid_lines}
payload=json.dumps(out,separators=(",",":"))
print("grid_lines:",len(grid_lines),"| payload MB: %.2f"%(len(payload)/1e6))
fpath=os.path.join(SC,"forces_240g.json")
forces=json.load(open(fpath)) if os.path.exists(fpath) else None
fpayload=json.dumps(forces,separators=(",",":")) if forces else "null"
if forces:print("forces sets:",forces["result_sets"],"| forces MB: %.2f"%(len(fpayload)/1e6))
tpl=open(os.path.join(SC,"viewer_template.html"),encoding="utf-8").read()
assert "/*__DATA__*/ null" in tpl and "/*__FORCES__*/ null" in tpl,"placeholder missing"
html=tpl.replace("/*__DATA__*/ null",payload).replace("/*__FORCES__*/ null",fpayload)
dest=os.path.join(SC,"cseye_viewer.html")
open(dest,"w",encoding="utf-8").write(html)
print("WROTE",dest,"%.2f MB"%(os.path.getsize(dest)/1e6))
