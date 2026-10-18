import sys,json,os
import cv2,numpy as np
from PIL import Image,ImageDraw
S={}
for l in open("scan.jsonl",encoding="utf-8"):
    r=json.loads(l); S[r["id"]]=r
def path(i): return os.path.join("figures",S[i]["image"].split("figures/",1)[1])
def tile(i,tw,th):
    im=Image.open(path(i)).convert("RGB"); im.thumbnail((tw,th))
    t=Image.new("RGB",(tw,th+14),"white"); t.paste(im,(0,14)); ImageDraw.Draw(t).text((2,1),f"{i} {im.size}",fill=(200,0,0)); return t
def sheet(ids,out,cols=2,tw=600,th=420):
    ts=[tile(i,tw,th) for i in ids]; rows=(len(ts)+cols-1)//cols
    s=Image.new("RGB",(tw*cols,(th+14)*rows),"white")
    for k,t in enumerate(ts): s.paste(t,((k%cols)*tw,(k//cols)*(th+14)))
    s.save(out)
if __name__=="__main__":
    sheet([int(x) for x in sys.argv[2].split(",")],sys.argv[1])
