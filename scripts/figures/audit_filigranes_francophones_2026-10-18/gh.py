import json,os
import cv2,numpy as np
from multiprocessing import Pool
def f(r):
    p=os.path.join("figures",r["image"].split("figures/",1)[1])
    a=cv2.imdecode(np.fromfile(p,np.uint8),1); g=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY); h,w=g.shape; n=h*w
    dark=(g<120).astype(np.uint8)
    near=cv2.dilate(dark,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(13,13)))
    pale=((g>=165)&(g<=238))
    iso=pale&(near==0)
    # blobs : on lisse pour garder les zones etendues (logo/texte fantome), pas le bruit
    m=cv2.morphologyEx(iso.astype(np.uint8),cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    k,lab,st,_=cv2.connectedComponentsWithStats(m)
    big=int(sum(st[i,4] for i in range(1,k) if st[i,4]>=0.0008*n)) if k>1 else 0
    lv=g[iso]
    if lv.size>200:
        hist=np.bincount(lv,minlength=256).astype(float); hist/=hist.sum(); top3=float(np.sort(hist)[-3:].sum())
    else: top3=1.0
    return dict(id=r["id"],iso=round(float(iso.sum()/n),4),big=round(big/n,4),iso_top3=round(top3,3))
if __name__=="__main__":
    rows=[json.loads(l) for l in open("scan.jsonl",encoding="utf-8")]
    with Pool(8) as P, open("gh.jsonl","w") as o:
        for x in P.imap_unordered(f,rows,chunksize=8): o.write(json.dumps(x)+"\n")
