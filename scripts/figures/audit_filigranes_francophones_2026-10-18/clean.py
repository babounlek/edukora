import sys,os,json
import cv2,numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,".")
import raw
def load(i): return cv2.imdecode(np.fromfile(raw.path(i),np.uint8),cv2.IMREAD_COLOR)
def chroma(a):
    a=a.astype(int); return a.max(2)-a.min(2)
def white_rects(a,rects):
    for x0,y0,x1,y1 in rects: a[max(y0,0):y1,max(x0,0):x1]=255
    return a
def kill_color(a,thr=18,minv=150):
    """efface les pixels colores pales ou satures (filigrane de couleur sur un contenu gris) -> blanc"""
    c=chroma(a); mn=a.min(2)
    m=(c>thr)&(mn>=minv)
    m=cv2.dilate(m.astype(np.uint8),np.ones((3,3),np.uint8))>0
    a=a.copy(); a[m]=255; return a
def to_gray(a):
    g=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY); return cv2.cvtColor(g,cv2.COLOR_GRAY2BGR)
def levels(a,lo,hi):
    """fond->blanc : ecrase le gris pale vers le blanc, garde l'encre"""
    g=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY).astype(np.float32)
    # aplatit l'eclairage : fond = dilatation + flou
    bg=cv2.GaussianBlur(cv2.dilate(g,np.ones((25,25),np.uint8)),(0,0),15)
    n=np.clip(g/np.maximum(bg,1)*255,0,255)
    o=np.clip((n-lo)*255/(hi-lo),0,255).astype(np.uint8); return cv2.cvtColor(o,cv2.COLOR_GRAY2BGR)
def keep_color_kill_pale_gray(a,hi=235,cmax=22):
    """contenu en couleur : on blanchit seulement le gris pale neutre (filigrane gris), pas les couleurs"""
    c=chroma(a); g=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY)
    m=(c<cmax)&(g>=170)
    a=a.copy(); a[m]=255; return a
def save(a,name): cv2.imencode(".png",a)[1].tofile(name)
def compare(i,a,out,tw=560,th=420):
    b=load(i)
    ims=[]
    for x in (b,a):
        im=Image.fromarray(cv2.cvtColor(x,cv2.COLOR_BGR2RGB)); im.thumbnail((tw,th)); ims.append(im)
    s=Image.new("RGB",(2*tw+6,th+14),"white")
    s.paste(ims[0],(0,14)); s.paste(ims[1],(tw+6,14)); ImageDraw.Draw(s).text((2,1),f"{i} avant / apres",fill=(200,0,0)); s.save(out)

def white_above(a,t=238):
    """ecrase en blanc les gris tres pales (fantomes >= t) ; ne touche ni l'encre ni les gris moyens"""
    g=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY); m=g>=t
    a=a.copy(); a[m]=255; return a
def enhance(a,lo=150,hi=245):
    g=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY).astype(np.float32)
    o=np.clip((g-lo)*255/(hi-lo),0,255).astype(np.uint8); return cv2.cvtColor(o,cv2.COLOR_GRAY2BGR)
def compare_enh(i,a,out,tw=560,th=420):
    b=load(i); ims=[]
    for x in (b,a):
        im=Image.fromarray(cv2.cvtColor(enhance(x),cv2.COLOR_BGR2RGB)); im.thumbnail((tw,th)); ims.append(im)
    s=Image.new("RGB",(2*tw+6,th+14),"white")
    s.paste(ims[0],(0,14)); s.paste(ims[1],(tw+6,14)); ImageDraw.Draw(s).text((2,1),f"{i} avant / apres (contraste etire)",fill=(200,0,0)); s.save(out)

def kill_pale_tint(a,minv=215,cmin=5,sdmax=6):
    """teintes tres pales lisses (logo fantome couleur) -> blanc ; les hachures/traits (forte variation locale) restent"""
    c=chroma(a); mn=a.min(2); g=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY).astype(np.float32)
    sm=cv2.blur(g,(9,9)); sm2=cv2.blur(g**2,(9,9)); sd=np.sqrt(np.maximum(sm2-sm**2,0))
    m=(mn>=minv)&(c>=cmin)&(sd<sdmax)
    m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))>0
    a=a.copy(); a[m]=255; return a
def sheet_cmp(ids,out,tw=560,th=420,cols=1):
    ims=[Image.open(f"out/cmp_{i}.png") for i in ids]
    s=Image.new("RGB",(ims[0].width*cols,sum(i.height for i in ims)//cols+10),"white"); y=0
    for k,im in enumerate(ims):
        s.paste(im,((k%cols)*im.width,(k//cols)*im.height))
    s.save(out)

def kill_color_keep_ink(a,thr=22,lum_white=165):
    """filigrane colore (saumon/orange) sur contenu gris : pixel colore -> gris ; clair -> blanc, sombre (encre dessous) -> garde sa luminance"""
    c=chroma(a); g=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY)
    m=(c>=thr); m=cv2.dilate(m.astype(np.uint8),np.ones((5,5),np.uint8))>0
    o=cv2.cvtColor(g,cv2.COLOR_GRAY2BGR); out=a.copy()
    gg=g.copy(); gg[gg>=lum_white]=255
    out[m]=cv2.cvtColor(gg,cv2.COLOR_GRAY2BGR)[m]
    return out

def kill_thick_gray(a,lo=110,hi=215,k=7,grow=4):
    """filigrane gris epais (texte diagonal) : composantes grises ou un disque de diametre k tient entierement -> blanc. l'encre fine (traits < k px) survit"""
    g=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY)
    m=((g>=lo)&(g<=hi)).astype(np.uint8)
    core=cv2.morphologyEx(m,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k)))
    big=cv2.dilate(core,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*grow+1,2*grow+1)))
    big=big&(g>=lo-30)
    out=a.copy(); out[big>0]=255; return out

def kill_flat_gray(a,lo=168,hi=208,sdmax=9,grow=3,floor=140):
    """aplat gris uniforme (texte diagonal) : pixels de gris ~constant dans un voisinage lisse -> blanc ; l'encre noire et les hachures (forte variance locale) restent"""
    g=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY).astype(np.float32)
    sm=cv2.blur(g,(7,7)); sm2=cv2.blur(g*g,(7,7)); sd=np.sqrt(np.maximum(sm2-sm*sm,0))
    m=((g>=lo)&(g<=hi)&(sd<sdmax)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    m=cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*grow+1,2*grow+1)))
    m=m&(g>=floor).astype(np.uint8)
    out=a.copy(); out[m>0]=255; return out

def kill_band_median(a,lo=165,hi=205,med=5,minarea=250,grow=2,floor=140):
    """texte filigrane gris : apres mediane (efface le bruit de scan), les composantes de gris ~constant et etendues -> blanc ; l'encre noire garde (hors bande)"""
    g=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY); gm=cv2.medianBlur(g,med)
    m=((gm>=lo)&(gm<=hi)).astype(np.uint8)
    k,lab,st,_=cv2.connectedComponentsWithStats(m,connectivity=8)
    keep=np.zeros_like(m)
    for i in range(1,k):
        if st[i,4]>=minarea: keep[lab==i]=1
    keep=cv2.dilate(keep,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*grow+1,2*grow+1)))
    keep=keep&(g>=floor).astype(np.uint8)
    out=a.copy(); out[keep>0]=255; return out
