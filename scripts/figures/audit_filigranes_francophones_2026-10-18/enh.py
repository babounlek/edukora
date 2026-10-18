import json,os,sys
import cv2,numpy as np
from PIL import Image,ImageDraw
S={}
for l in open("scan.jsonl",encoding="utf-8"):
    r=json.loads(l); S[r["id"]]=r
def load(i):
    r=S[i]; return cv2.imdecode(np.fromfile(os.path.join("figures",r["image"].split("figures/",1)[1]),np.uint8),1)
def mid(i):
    g=cv2.cvtColor(load(i),cv2.COLOR_BGR2GRAY); return float(((g>=60)&(g<=170)).mean())
def tile(i,tw=400,th=300):
    a=load(i); g=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY).astype(np.float32)
    e=np.clip((g-150)*255/95,0,255).astype(np.uint8)   # le pale ressort, le blanc reste blanc
    im=Image.fromarray(e).convert("RGB"); im.thumbnail((tw,th))
    t=Image.new("RGB",(tw,th+14),"white"); t.paste(im,(0,14)); ImageDraw.Draw(t).text((2,1),f"{i} {S[i]['lesson'][-30:]}",fill=(200,0,0)); return t
def sheet(ids,out,cols=3):
    ts=[tile(i) for i in ids]; rows=(len(ts)+cols-1)//cols
    s=Image.new("RGB",(400*cols,314*rows),"white")
    for k,t in enumerate(ts): s.paste(t,((k%cols)*400,(k//cols)*314))
    s.save(out)
if __name__=="__main__":
    ids=json.load(open("cand_ids.json"))
    M={i:mid(i) for i in ids}; json.dump(M,open("mid.json","w"))
    trait=[i for i in ids if M[i]<0.20]; photo=[i for i in ids if M[i]>=0.20]
    print("trait",len(trait),"photo/demi-teinte",len(photo))
    json.dump(dict(trait=trait,photo=photo),open("cand_split.json","w"))
    for k in range(0,len(trait),15): sheet(trait[k:k+15],f"rev/t{k//15:02d}.png")
