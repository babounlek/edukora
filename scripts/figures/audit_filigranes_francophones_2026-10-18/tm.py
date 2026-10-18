import json,os,sys
import cv2,numpy as np
from multiprocessing import Pool
T={n:cv2.cvtColor(cv2.imdecode(np.fromfile(f"tpl/{n}.png",np.uint8),1),cv2.COLOR_BGR2GRAY) for n in ("url_bleu","banner","orni")}
def rd(p): return cv2.imdecode(np.fromfile(p,np.uint8),cv2.IMREAD_GRAYSCALE)
def best(g,t):
    bs,bsc=0,-1
    for s in (0.35,0.45,0.55,0.65,0.75,0.85,1.0,1.15,1.3,1.5,1.75,2.0):
        tt=cv2.resize(t,None,fx=s,fy=s,interpolation=cv2.INTER_AREA if s<1 else cv2.INTER_CUBIC)
        if tt.shape[0]>=g.shape[0] or tt.shape[1]>=g.shape[1]: continue
        r=cv2.matchTemplate(g,tt,cv2.TM_CCOEFF_NORMED); v=float(r.max())
        if v>bsc: bsc,bs=v,s
    return bsc,bs
def f(r):
    g=rd(os.path.join("figures",r["image"].split("figures/",1)[1]))
    out=dict(id=r["id"])
    for n,t in T.items():
        sc,s=best(g,t); out[n]=round(sc,3); out[n+"_s"]=s
    return out
if __name__=="__main__":
    rows=[json.loads(l) for l in open("scan.jsonl",encoding="utf-8")]
    with Pool(8) as P, open("tm.jsonl","w") as o:
        for x in P.imap_unordered(f,rows,chunksize=8): o.write(json.dumps(x)+"\n")
