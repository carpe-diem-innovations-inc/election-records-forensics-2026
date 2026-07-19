import os, sys, struct, plistlib, json, datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = os.environ.get("EI_WORKSPACE") or os.getcwd()
EXTRACT = os.path.join(WS, "extracted")
DATA = os.path.join(WS, "data")

def parse_appledouble(data):
    """Return dict of extended attributes {name: raw_bytes}."""
    out = {}
    if len(data) < 26 or struct.unpack(">I", data[:4])[0] != 0x00051607:
        return out
    # locate ATTR magic
    idx = data.find(b"ATTR")
    if idx == -1:
        return out
    try:
        # attr_header
        magic, debug_tag, total_size, data_start, data_length = struct.unpack(">IIIII", data[idx:idx+20])
        # reserved[3] then flags(2) num_attrs(2)
        flags, num_attrs = struct.unpack(">HH", data[idx+32:idx+36])
        p = idx + 36
        for _ in range(num_attrs):
            if p + 11 > len(data):
                break
            a_off, a_len, a_flags, a_namelen = struct.unpack(">IIHB", data[p:p+11])
            name = data[p+11:p+11+a_namelen].split(b"\x00")[0].decode("utf-8", "replace")
            # offsets are from start of the AppleDouble ATTR region base = idx? empirically from file start
            val = data[a_off:a_off+a_len]
            out[name] = val
            # advance: entry is 11 + namelen, padded to 4 bytes
            entry_len = 11 + a_namelen
            entry_len = (entry_len + 3) & ~3
            p += entry_len
    except Exception as e:
        out["_parse_error"] = str(e).encode()
    return out

def decode_wherefroms(raw):
    try:
        pl = plistlib.loads(raw)
        return pl
    except Exception:
        # sometimes stored as bplist inside
        i = raw.find(b"bplist00")
        if i >= 0:
            try:
                return plistlib.loads(raw[i:])
            except Exception:
                pass
    return None

def decode_quarantine(raw):
    try:
        s = raw.split(b"\x00")[0].decode("utf-8","replace")
        parts = s.split(";")
        d = {"raw": s}
        if len(parts) >= 4:
            d["flags"] = parts[0]
            try:
                ts = int(parts[1], 16)
                dt = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
                d["download_time_utc"] = dt.replace(tzinfo=None).isoformat()+"Z"
                d["download_time_epoch"] = ts
            except Exception:
                d["timestamp_raw"] = parts[1]
            d["agent"] = parts[2]
            d["event_uuid"] = parts[3]
        return d
    except Exception as e:
        return {"error": str(e)}

results = []
for root, dirs, files in os.walk(EXTRACT):
    dirs.sort(); files.sort()  # deterministic traversal: NTFS returns sorted entries, ext4 does not
    for fn in files:
        if not fn.startswith("._"):
            continue
        full = os.path.join(root, fn)
        rel = os.path.relpath(full, EXTRACT).replace("\\","/")
        with open(full, "rb") as f:
            data = f.read()
        xattrs = parse_appledouble(data)
        target = fn[2:]  # the file this sidecar describes
        rec = {"sidecar": rel, "target": target, "xattr_names": sorted(xattrs.keys()), "size": len(data)}
        if "com.apple.quarantine" in xattrs:
            rec["quarantine"] = decode_quarantine(xattrs["com.apple.quarantine"])
        if "com.apple.metadata:kMDItemWhereFroms" in xattrs:
            wf = decode_wherefroms(xattrs["com.apple.metadata:kMDItemWhereFroms"])
            rec["where_froms"] = wf
        # capture any other interesting keys raw-ish
        others = {k: (v[:120].hex() if not k.startswith("com.apple.quarantine") else None)
                  for k,v in xattrs.items()
                  if k not in ("com.apple.quarantine","com.apple.metadata:kMDItemWhereFroms")}
        if others:
            rec["other_xattrs_hexpreview"] = others
        results.append(rec)

with open(os.path.join(DATA, "macos_xattrs.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(results, f, indent=2, default=str)

# ---- .DS_Store: Finder folder-state files can retain names of folders that were
# ---- renamed or removed before zipping (curation residue). Decode every entry name.
from ds_store import DSStore

dsstore_records = []
for root, dirs, files in os.walk(EXTRACT):
    dirs.sort(); files.sort()
    for fn in files:
        if fn != ".DS_Store":
            continue
        full = os.path.join(root, fn)
        rel = os.path.relpath(full, EXTRACT).replace("\\", "/")
        rec = {"path": rel, "size": os.path.getsize(full)}
        try:
            with DSStore.open(full, "r") as d:
                rec["entry_names"] = sorted({e.filename for e in d})
        except Exception as e:
            rec["error"] = str(e)
        dsstore_records.append(rec)

with open(os.path.join(DATA, "dsstore.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(dsstore_records, f, indent=2, default=str)

# Summary
agents = {}
times = []
wheres = 0
q = 0
for r in results:
    if "quarantine" in r:
        q += 1
        a = r["quarantine"].get("agent","?")
        agents[a] = agents.get(a,0)+1
        if "download_time_utc" in r["quarantine"]:
            times.append(r["quarantine"]["download_time_utc"])
    if r.get("where_froms"):
        wheres += 1

print(f"AppleDouble sidecars parsed: {len(results)}")
print(f"  with com.apple.quarantine: {q}")
print(f"  with kMDItemWhereFroms:    {wheres}")
print(f"  download agents: {agents}")
print(f"  all xattr key sets seen:")
keysets = {}
for r in results:
    ks = ", ".join(r["xattr_names"]) or "(none)"
    keysets[ks] = keysets.get(ks,0)+1
for ks,c in sorted(keysets.items(), key=lambda x:-x[1]):
    print(f"     x{c}: {ks}")
if times:
    print(f"\n  quarantine download times range: {min(times)}  ->  {max(times)}")

print(f"\n.DS_Store files decoded: {len(dsstore_records)}")
for r in dsstore_records:
    names = r.get("entry_names", [])
    print(f"  {r['path']}: {len(names)} entry name(s)")
    for n in names:
        print(f"     - {n}")
