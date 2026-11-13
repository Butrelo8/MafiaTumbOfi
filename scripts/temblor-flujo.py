# Reference-free tremble measure: residual of each frame against the mean of its two optical-flow-warped neighbours, per crop (2026-11-12, docs/temblor-texturas.md).
# uv run -q --with numpy --with opencv-python-headless python -I scripts/temblor-flujo.py <frame dir f_####.png> <first> <last> '{"name":(x,y,w,h)}'
# motion-compensated residual per crop for a frame dir, frames a..b (centre frames)
import sys, numpy as np, cv2
d=sys.argv[1]; a,b=int(sys.argv[2]),int(sys.argv[3]); crops=eval(sys.argv[4])
dis=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
def L(i): return cv2.imread(f"{d}/f_{i:04d}.png")
def warp(src,flow):
    h,w=flow.shape[:2]; gx,gy=np.meshgrid(np.arange(w),np.arange(h))
    return cv2.remap(src,(gx+flow[...,0]).astype(np.float32),(gy+flow[...,1]).astype(np.float32),cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
fr={i:L(i) for i in range(a-1,b+2)}; gr={i:cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for i,f in fr.items()}
acc={k:[] for k in crops}
for i in range(a,b+1):
    cur=fr[i].astype(np.float32)
    wp=warp(fr[i-1],dis.calc(gr[i],gr[i-1],None)).astype(np.float32); wn=warp(fr[i+1],dis.calc(gr[i],gr[i+1],None)).astype(np.float32)
    r=np.abs(cur-(wp+wn)/2).mean(2)
    for k,(x,y,w,h) in crops.items(): acc[k].append(r[y:y+h,x:x+w].mean())
print(d.split('/')[-1], " ".join(f"{k}={np.mean(v):.3f}" for k,v in acc.items()))
