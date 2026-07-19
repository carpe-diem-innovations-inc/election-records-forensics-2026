import os, re, sys, shutil, glob, json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = os.environ.get("EI_WORKSPACE") or os.getcwd()
SRC_OCR = os.path.join(WS, "data", "ocr")
OUT = os.path.join(WS, "data_public")
if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(os.path.join(OUT, "metadata"))
os.makedirs(os.path.join(OUT, "ocr_intelligence"))

# 1) forensic metadata — no third-party PII, copy as-is
for fn in ["inventory.csv","duplicates.json","macos_xattrs.json","dsstore.json","pdf_metadata.json",
           "redaction_leaks.json","revision_recovery.json","consolidated_findings.json"]:
    p = os.path.join(WS,"data",fn)
    if os.path.exists(p): shutil.copy(p, os.path.join(OUT,"metadata",fn))

# 2) intelligence OCR — publish scrubbed; Michigan FBI witness memos are EXCLUDED (private citizens)
INTEL_KEYS = ["NICM_ChinaStepsToInfluenceElection","Note_-_Sensitive_PRC_Reporting",
 "200M_Voter_Records_Compromised","18_States_Memo","PRC_","Summary_-_clean",
 "CIA_Note_-_Venezuela_Machines","EMAIL_ICA.CommentsReMinorityView",
 "EMAIL_RE_Please_coord","US_Voter_Registration__for_6_States"]
# Michigan / private-citizen files: never republished verbatim
EXCLUDE = ["FBIMichigan","Muskego","RELEASE_MARKED","265_0000001","0000001","196_","233_",
           "Voter_Fraud_Spreadsheet","GBI_Strategies","PIN_"]

PHONE = re.compile(r'\b\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b')
SSN   = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
DOBV  = re.compile(r'((?:date of birth|DOB|SSAN|social security(?: account)? number)\s*[:#]?\s*)([0-9/\-]{3,})', re.I)
EMAIL = re.compile(r'\b[\w.+-]+@[\w-]+\.[\w.-]+\b')
STREET= re.compile(r'\b\d{1,6}\s+([A-Z][a-z]+\s+){1,3}(St|Street|Ave|Avenue|Rd|Road|Blvd|Dr|Drive|Ln|Lane|Ct|Court|Way)\b')

def keep_email(m):
    e = m.group(0).lower()
    return e if e.endswith(".gov") else "[email redacted]"

def scrub(t):
    log = {"phone":0,"ssn":0,"dob_value":0,"email":0,"street":0}
    def sub(pat, repl, key, s):
        def f(m):
            log[key]+=1; return repl(m) if callable(repl) else repl
        return pat.sub(f, s)
    t = sub(SSN, "[SSN redacted]", "ssn", t)
    t = sub(PHONE, "[phone redacted]", "phone", t)
    t = DOBV.sub(lambda m: (log.__setitem__("dob_value",log["dob_value"]+1) or m.group(1)+"[redacted]"), t)
    t = sub(EMAIL, keep_email, "email", t)
    t = sub(STREET, "[address redacted]", "street", t)
    return t, log

def wanted(fn):
    if any(x in fn for x in EXCLUDE): return False
    return any(k in fn for k in INTEL_KEYS)

report = {}
for p in sorted(glob.glob(os.path.join(SRC_OCR,"*.ocr.txt"))):
    fn = os.path.basename(p)
    if not wanted(fn): continue
    t = open(p, encoding="utf-8", errors="replace").read()
    scrubbed, log = scrub(t)
    open(os.path.join(OUT,"ocr_intelligence",fn),"w",encoding="utf-8",newline="\n").write(scrubbed)
    if any(log.values()): report[fn]=log

with open(os.path.join(OUT,"SCRUB_LOG.json"),"w",encoding="utf-8",newline="\n") as f:
    json.dump(report, f, indent=2)

intel_ct = len(os.listdir(os.path.join(OUT,"ocr_intelligence")))
excluded = sorted({os.path.basename(p) for p in glob.glob(os.path.join(SRC_OCR,"*.ocr.txt"))
                   if any(x in os.path.basename(p) for x in EXCLUDE)})
print(f"metadata files: {len(os.listdir(os.path.join(OUT,'metadata')))}")
print(f"intelligence OCR published (scrubbed): {intel_ct}")
print(f"Michigan/private-citizen OCR EXCLUDED from publication: {len(excluded)}")
print("scrub actions:", json.dumps(report, indent=2) if report else "none needed (source already redacted)")
