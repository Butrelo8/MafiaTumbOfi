# Tremble vs the 1024-sample reference on the figures crop (blender/temblor.py variant `ref`): hp = RMS of the second temporal difference of (frame - ref), so camera motion cancels. Columns for other crops are meaningless (the reference only covers the figures).
import sys, numpy as np, cv2, os, json
R="/mnt/e/Cursor Projects/MTO/blender/render/transicion/temblor"
F0,F1=164,187
CROPS={"figuras":(560,230,260,200),"carretera":(60,330,320,240),"trasera":(520,420,360,260)}
def load(v):
    out=[]
    for f in range(F0,F1+1):
        im=cv2.imread(f"{R}/{v}/f_{f:04d}.png")
        out.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32))
    return np.stack(out)
def crop(a,c): x,y,w,h=c; return a[:,y:y+h,x:x+w]
def metrics(a,ref):
    r={}
    for k,c in CROPS.items():
        A=crop(a,c); Rf=crop(ref,c); e=A-Rf
        hp=e[1:-1]-(e[:-2]+e[2:])/2             # 2nd temporal difference of the error: motion cancels, only frame-to-frame noise stays
        d2=A[1:-1]-(A[:-2]+A[2:])/2             # same on the frame itself: includes the real motion
        r[k]=dict(tstd=float(e.std(0).mean()), hp=float(np.sqrt((hp**2).mean())), rms=float(np.sqrt((e**2).mean())), d2=float(np.abs(d2).mean()))
    return r
if __name__=="__main__":
    ref=load("ref"); rows={}
    for v in sys.argv[1:]:
        if not os.path.isdir(f"{R}/{v}"): continue
        rows[v]=metrics(load(v),ref)
    # reference itself vs a shifted-by-nothing is 0; print table
    print("variant\t"+"\t".join(f"{k}:hp/tstd/rms/d2" for k in CROPS))
    for v,r in rows.items():
        print(v+"\t"+"\t".join("/".join(f"{r[k][m]:.2f}" for m in ("hp","tstd","rms","d2")) for k in CROPS))
