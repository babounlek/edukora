import json,sys,os,re,subprocess,tempfile
import numpy as np, cv2
from multiprocessing import Pool
EXE=r"C:\Program Files\Tesseract-OCR\tesseract.exe"
MOTS=re.compile(r"gcerevis|revision|kawlo|concours|cameroon\.?com|cameroon|\.com|www|download|play\s*store|past\s+questions|orniformation|annales|telechar|t[ée]l[ée]char",re.I)
def lire(p):
    return cv2.imdecode(np.fromfile(p,np.uint8),cv2.IMREAD_COLOR)
TMP=os.path.join(os.getcwd(),"tmp_ocr")
def ocr(img):
    g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    f=2 if max(g.shape)<1200 else 1
    g=cv2.resize(g,None,fx=f,fy=f,interpolation=cv2.INTER_CUBIC)
    fd,t=tempfile.mkstemp(suffix=".png",dir=TMP); os.close(fd)
    cv2.imencode(".png",g)[1].tofile(t)
    try:
        r=subprocess.run([EXE,t,"stdout","--psm","11","-l","fra+eng"],capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=120)
        return r.stdout or ""
    except Exception as e: return "[err]"
    finally:
        try: os.remove(t)
        except OSError: pass
def feats(r):
    p=os.path.join("figures",r["image"].split("figures/",1)[1])
    img=lire(p)
    if img is None: return dict(id=r["id"],err="illisible")
    h,w=img.shape[:2]; g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    b,gc,rc=[img[:,:,i].astype(int) for i in (0,1,2)]
    n=h*w
    blanc=(g>=252).mean()
    nonblanc=(g<235).sum()
    pale=((g>=150)&(g<235)&((np.maximum(np.maximum(b,gc),rc)-np.minimum(np.minimum(b,gc),rc))<30)).sum()/n
    bleu=((b>200)&(rc<70)&(gc<70)).sum()
    # bruit hors-trait : pixels gris tres pale (225-250) = voile de scan
    voile=((g>=215)&(g<250)).mean()
    txt=ocr(img)
    hits=sorted(set(m.group(0).lower() for m in MOTS.finditer(txt)))
    return dict(id=r["id"],image=r["image"],lesson=r["lesson"],w=w,h=h,blanc=round(blanc,4),pale=round(float(pale),4),bleu=int(bleu),voile=round(float(voile),4),hits=hits,txt=txt[:400])
if __name__=="__main__":
    TMP=os.path.join(os.getcwd(),"tmp_ocr"); os.makedirs(TMP,exist_ok=True)
    rows=json.load(open("manifeste.json"))
    with Pool(8) as P, open("scan.jsonl","w",encoding="utf-8") as out:
        for i,f in enumerate(P.imap_unordered(feats,rows,chunksize=4)):
            out.write(json.dumps(f,ensure_ascii=False)+"\n"); out.flush()
