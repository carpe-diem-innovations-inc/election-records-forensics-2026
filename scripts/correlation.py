import json, os, sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WS=os.path.dirname(__file__)

# States/DC named in the WHTF public statement bullet list
named = ["AK","AR","CO","CT","DC","FL","GA","IA","KS","MD","MI","NY","NC","OH","OK","RI"]

# DOJ sued (resisted data demands) — from Brennan/UW-Madison trackers (explicit names captured)
sued = {"CA","MI","MN","NY","NH","PA","AZ","CT","DE","MD","NM","RI","VT","WA","CO","HI","MA","NV","UT","OK","KY","WV","NJ","VA","DC"}
# States that COMPLIED (handed over full rolls incl SSN/DL)
complied = {"AL","AK","AR","FL","IN","IA","LA","MS","NE","OH","OK","SC","SD","TN","TX","WY"}

# 2026 battlegrounds
senate_bg = {"OH","ME","NC","GA","MI"}
gov_bg = {"AZ","WI","GA","IA","NV"}

# rough partisan control of state govt / typical lean (for interpretation only)
lean = {"AK":"R","AR":"R","CO":"D","CT":"D","DC":"D","FL":"R","GA":"R/lean","IA":"R",
        "KS":"R","MD":"D","MI":"D/swing","NY":"D","NC":"R/swing","OH":"R","OK":"R","RI":"D"}

rows=[]
for s in named:
    posture = "sued/resisted" if s in sued else ("complied" if s in complied else "—")
    bg=[]
    if s in senate_bg: bg.append("Sen")
    if s in gov_bg: bg.append("Gov")
    rows.append((s, posture, ",".join(bg) or "—", lean.get(s,"?")))

print("Named state | DOJ posture   | 2026 battleground | lean")
print("-"*60)
for s,p,b,l in rows:
    print(f"  {s:3s}      | {p:13s} | {b:16s} | {l}")

n_sued=sum(1 for s in named if s in sued)
n_comp=sum(1 for s in named if s in complied)
n_neither=sum(1 for s in named if s not in sued and s not in complied)
n_bg=sum(1 for s in named if s in senate_bg or s in gov_bg)
print("\nSUMMARY of the 16 named entities:")
print(f"  sued/resisted DOJ data demand : {n_sued}  -> {[s for s in named if s in sued]}")
print(f"  complied (gave data)          : {n_comp}  -> {[s for s in named if s in complied]}")
print(f"  neither/unclear               : {n_neither}  -> {[s for s in named if s not in sued and s not in complied]}")
print(f"  2026 marquee battleground     : {n_bg}  -> {[s for s in named if s in senate_bg or s in gov_bg]}")
print(f"\n  named that are D-leaning & resisted: {[s for s in named if s in sued and lean.get(s,'').startswith('D')]}")
print(f"  named that are R-leaning & complied: {[s for s in named if s in complied and lean.get(s,'').startswith('R')]}")
