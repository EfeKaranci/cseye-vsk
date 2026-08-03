"""Keep all load cases + a curated set of combos for the demo artifact.
Preserve the full extract separately for the bridge/git."""
import json, os, shutil
SC=r"C:\Users\ekaranci\AppData\Local\Temp\claude\c--Analysis-WC2026\da951d2a-a94b-4be2-a4a4-4acf28fa31ac\scratchpad"
f=json.load(open(os.path.join(SC,"forces_240g.json")))
shutil.copyfile(os.path.join(SC,"forces_240g.json"),os.path.join(SC,"forces_40hy_full.json"))
kinds=f.get("result_kinds",{})
CURATED_COMBOS=["CSA ENVELOPE","ENV ASD-Non Seismic","W_USER-ENV","ULS-2 - 1.2D + 1.6L",
                "ULS-1 - 1.4D","ASD-2-D+L","1.2D+0.5L+1.0Ex_ELF","1.2D+0.5L+1.0Ey_ELF"]
keep=[n for n in f["result_sets"] if kinds.get(n,"case")=="case"] + \
     [n for n in f["result_sets"] if kinds.get(n)=="combo" and n in CURATED_COMBOS]
keepset=set(keep)
cf={}
for col,d in f["col_forces"].items():
    sub={k:v for k,v in d.items() if k in keepset}
    if sub: cf[col]=sub
rx={}
for j,r in f["reactions"].items():
    sub={k:v for k,v in r["cases"].items() if k in keepset}
    rx[j]={"x":r["x"],"y":r["y"],"z":r["z"],"cases":sub}
out={"model":f["model"],"units":f["units"],"result_sets":keep,
     "result_kinds":{n:kinds.get(n,"case") for n in keep},"col_forces":cf,"reactions":rx}
json.dump(out,open(os.path.join(SC,"forces_240g.json"),"w"),separators=(",",":"))
sz=os.path.getsize(os.path.join(SC,"forces_240g.json"))/1e6
nc=sum(1 for n in keep if out["result_kinds"][n]=="case");nk=len(keep)-nc
print(f"trimmed forces: {sz:.2f} MB | {nc} cases + {nk} combos")
print("combos kept:",[n for n in keep if out['result_kinds'][n]=='combo'])
