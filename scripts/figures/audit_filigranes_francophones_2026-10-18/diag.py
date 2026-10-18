import json,os,sys
import cv2,numpy as np
from PIL import Image,ImageDraw
S={};G={}
for l in open("scan.jsonl",encoding="utf-8"):
    r=json.loads(l); S[r["id"]]=r
for l in open("gh.jsonl"): x=json.loads(l); G[x["id"]]=x
def tile(i,tw=300,th=230):
    r=S[i]; a=cv2.imdecode(np.fromfile(os.path.join("figures",r["image"].split("figures/",1)[1]),np.uint8),1)
    g=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY)
    dark=(g<120).astype(np.uint8); near=cv2.dilate(dark,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(13,13)))
    iso=((g>=165)&(g<=238)&(near==0)).astype(np.uint8)
    m=cv2.morphologyEx(iso,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    o=a.copy(); o[m>0]=(0.5*o[m>0]+0.5*np.array([0,0,255])).astype(np.uint8)
    im=Image.fromarray(cv2.cvtColor(o,cv2.COLOR_BGR2RGB)); im.thumbnail((tw,th))
    t=Image.new("RGB",(tw,th+14),"white"); t.paste(im,(0,14)); ImageDraw.Draw(t).text((2,1),f"{i} {r['lesson'][-26:]}",fill=(0,0,0)); return t
def sheet(ids,out,cols=4):
    ts=[tile(i) for i in ids]; rows=(len(ts)+cols-1)//cols
    s=Image.new("RGB",(300*cols,244*rows),"white")
    for k,t in enumerate(ts): s.paste(t,((k%cols)*300,(k//cols)*244))
    s.save(out)
if __name__=="__main__":
    ids=sorted([i for i,x in G.items() if x["iso_top3"]<0.6 and x["big"]>=0.01],key=lambda i:(S[i]["lesson"],i))
    json.dump(ids,open("cand_ids.json","w"))
    for k in range(0,len(ids),24): sheet(ids[k:k+24],f"rev/c{k//24:02d}.png")
    print(len(ids),(len(ids)+23)//24)
