import os, re, sys, numpy as np, fitz
from rapidocr_onnxruntime import RapidOCR

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = os.environ.get("EI_WORKSPACE") or os.getcwd()
EXTRACT = os.path.join(WS, "extracted")
OUT = os.path.join(WS, "data", "ocr")
os.makedirs(OUT, exist_ok=True)

# high-value intelligence docs (substance of the China/PRC/vote-change question)
TARGETS = [
 "NICM_ChinaStepsToInfluenceElection",
 "Note - Sensitive PRC Reporting",
 "200M Voter Records Compromised",
 "18 States Memo",
 "PRC Analsyis on US Voter Registration",
 "PRC Target 2024 Election 2023",
 "US Voter Registration  for 6 States",
 "PRC U.S. Presidential Election-Related Intelligence",
 "PRC US Voter Data 7 States 2023",
 "PRC Collection of US VoterMilitaryData",
 "Summary - clean - declass marked PART 1",
 "Summary - clean - declass marked PART 2",
 "Summary - clean - declass marked PART 3",
 "CIA Note - Venezuela Machines",
 "EMAIL_ICA.CommentsReMinorityView",
 "EMAIL_RE Please coord by COB 9.1",
]

engine = RapidOCR()

def wanted(fn):
    return any(t in fn for t in TARGETS)

paths = []
for root, dirs, files in os.walk(EXTRACT):
    dirs.sort(); files.sort()  # deterministic traversal (also fixes first-seen basename dedupe below)
    if "__MACOSX" in root: continue
    for fn in files:
        if fn.lower().endswith(".pdf") and wanted(fn):
            paths.append(os.path.join(root,fn))
# dedupe by basename
seen=set(); uniq=[]
for p in paths:
    b=os.path.basename(p)
    if b not in seen: seen.add(b); uniq.append(p)

print(f"OCR targets: {len(uniq)}", flush=True)
for p in uniq:
    fn=os.path.basename(p)
    outp=os.path.join(OUT, re.sub(r'[^\w.-]','_',fn)+".ocr.txt")
    if os.path.exists(outp):
        print("skip (done):",fn,flush=True); continue
    doc=fitz.open(p)
    alltext=[]
    for i,page in enumerate(doc):
        pix=page.get_pixmap(dpi=220, colorspace=fitz.csRGB)
        img=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,3)
        res,_=engine(img)
        lines=[t for _,t,_ in res] if res else []
        alltext.append(f"--- page {i+1} ---\n"+"\n".join(lines))
    doc.close()
    open(outp,"w",encoding="utf-8",newline="\n").write("\n".join(alltext))
    txt="\n".join(alltext)
    print(f"OCR done: {fn}  chars={len(txt)}",flush=True)
print("ALL OCR COMPLETE",flush=True)
