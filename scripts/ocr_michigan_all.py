import os, re, sys, numpy as np, fitz
from rapidocr_onnxruntime import RapidOCR
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WS=os.environ.get("EI_WORKSPACE") or os.getcwd()
EXTRACT=os.path.join(WS,"extracted"); OUT=os.path.join(WS,"data","ocr")
os.makedirs(OUT, exist_ok=True)
engine=RapidOCR()
todo=[]
for root, dirs, files in os.walk(EXTRACT):
    dirs.sort(); files.sort()
    if "__MACOSX" in root or "Michigan" not in root: continue
    for fn in files:
        if fn.lower().endswith(".pdf"):
            outp=os.path.join(OUT,re.sub(r'[^\w.-]','_',fn)+".ocr.txt")
            if not os.path.exists(outp): todo.append((os.path.join(root,fn),fn,outp))
print(f"remaining Michigan docs to OCR: {len(todo)}",flush=True)
for path,fn,outp in todo:
    doc=fitz.open(path); out=[]
    for i,p in enumerate(doc):
        pix=p.get_pixmap(dpi=220,colorspace=fitz.csRGB)
        img=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,3)
        res,_=engine(img); out.append(f"--- page {i+1} ---\n"+("\n".join(t for _,t,_ in res) if res else ""))
    doc.close(); open(outp,"w",encoding="utf-8",newline="\n").write("\n".join(out))
    print(f"done {fn}  chars={sum(len(x) for x in out)}",flush=True)
print("ALL MICHIGAN OCR COMPLETE",flush=True)
