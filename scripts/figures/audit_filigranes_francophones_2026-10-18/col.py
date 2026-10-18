import json,os
import cv2,numpy as np
from multiprocessing import Pool
def f(r):
    p=os.path.join("figures",r["image"].split("figures/",1)[1])
    a=cv2.imdecode(np.fromfile(p,np.uint8),1); h,w=a.shape[:2]; n=h*w
    b,g,rr=[a[:,:,i].astype(int) for i in (0,1,2)]
    out=dict(id=r["id"])
    # URL bleue : composantes larges et basses de bleu vif
    m=((b>170)&(rr<100)&(g<100)).astype(np.uint8)
    out["blue_n"]=int(m.sum())
    best=None
    if m.sum()>150:
        d=cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_RECT,(15,5)))
        k,lab,st,_=cv2.connectedComponentsWithStats(d)
        for i in range(1,k):
            x,y,ww,hh,ar=st[i]
            nb=int(m[y:y+hh,x:x+ww].sum())
            if ww>=70 and hh<=45 and nb>=150 and ww/hh>=4:
                if best is None or nb>best[4]: best=(int(x),int(y),int(ww),int(hh),nb)
    out["url_box"]=best
    # teintes pales non plates
    mx=np.maximum(np.maximum(b,g),rr); mn=np.minimum(np.minimum(b,g),rr); ch=mx-mn
    tint=(ch>=14)&(ch<=90)&(mn>=150)
    out["tint"]=round(float(tint.sum()/n),4)
    if tint.sum()>50:
        q=(a[tint]//8).astype(np.int32); key=q[:,0]*1024+q[:,1]*32+q[:,2]
        u,c=np.unique(key,return_counts=True)
        out["tint_top3"]=round(float(np.sort(c)[-3:].sum()/c.sum()),3); out["tint_ncol"]=int(len(u))
    else: out["tint_top3"]=1.0; out["tint_ncol"]=0
    # bande drapeau (vert+rouge+jaune satures) dans le haut
    top=a[:max(int(h*0.12),30)]
    tb,tg,tr=[top[:,:,i].astype(int) for i in (0,1,2)]
    ye=((tr>200)&(tg>170)&(tb<90)).sum(); re=((tr>170)&(tg<70)&(tb<70)).sum(); gr=((tg>110)&(tr<70)&(tb<90)).sum()
    out["flag"]=[int(ye),int(re),int(gr)]
    return out
if __name__=="__main__":
    rows=[json.loads(l) for l in open("scan.jsonl",encoding="utf-8")]
    with Pool(8) as P, open("col.jsonl","w") as o:
        for x in P.imap_unordered(f,rows,chunksize=8): o.write(json.dumps(x)+"\n")
