"""Unit tests for the parsing primitives.

The pipeline scripts are deliberately flat (no package structure — anyone can read
top to bottom), so importing one executes its file-walk against $EI_WORKSPACE.
The fixture points EI_WORKSPACE at an empty temp dir first, which makes every
import a harmless no-op run, then the tests exercise the pure functions.
"""
import importlib.util
import json
import os
import sys
import tempfile

SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")

_ws = tempfile.mkdtemp(prefix="ei_tests_")
os.makedirs(os.path.join(_ws, "data"), exist_ok=True)
os.environ["EI_WORKSPACE"] = _ws
os.environ.setdefault("EI_CORPUS", os.path.join(_ws, "corpus"))


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(SCRIPTS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


macos = load("macos_forensics")
pdff = load("pdf_forensics")
scrub = load("scrub_and_pack")
tbv = load("trust_but_verify")


def test_decode_quarantine_known_string():
    raw = b"0083;687892ab;Chrome;12345678-ABCD-EF00-1234-56789ABCDEF0\x00"
    d = macos.decode_quarantine(raw)
    assert d["agent"] == "Chrome"
    assert d["event_uuid"] == "12345678-ABCD-EF00-1234-56789ABCDEF0"
    assert d["download_time_epoch"] == int("687892ab", 16)
    assert d["download_time_utc"].endswith("Z")


def test_parse_appledouble_rejects_garbage():
    assert macos.parse_appledouble(b"not an appledouble file at all") == {}
    assert macos.parse_appledouble(b"") == {}


def test_pdf_dates_formats():
    assert pdff.pdf_dates("D:20260714140059-04'00'") == "2026-07-14T14:00:59-04'00'"
    assert pdff.pdf_dates(None) is None
    assert pdff.pdf_dates("D:2026") == "2026-01-01T01:01:01"


def test_xmp_prefixed_clark_notation():
    assert pdff.xmp_prefixed("{http://ns.adobe.com/xap/1.0/}CreatorTool") == "xmp:CreatorTool"
    assert pdff.xmp_prefixed("{http://purl.org/dc/elements/1.1/}creator") == "dc:creator"
    assert pdff.xmp_prefixed("already:prefixed") == "already:prefixed"


def test_scrub_masks_pii_but_keeps_gov_email():
    text = ("SSN 123-45-6789, call (555) 123-4567, "
            "mail officer@fbi.gov or private.person@gmail.com")
    out, log = scrub.scrub(text)
    assert "123-45-6789" not in out and "[SSN redacted]" in out
    assert "123-4567" not in out and "[phone redacted]" in out
    assert "officer@fbi.gov" in out
    assert "private.person@gmail.com" not in out and "[email redacted]" in out
    assert log["ssn"] == 1 and log["phone"] == 1 and log["email"] >= 1


def test_wanted_excludes_private_citizen_files():
    assert not scrub.wanted("FBIMichigan Witness Interview Memo RELEASE_MARKED.pdf.ocr.txt")
    assert not scrub.wanted("Voter_Fraud_Spreadsheet - RELEASE_MARKED.pdf.ocr.txt")
    assert scrub.wanted("NICM_ChinaStepsToInfluenceElection_16OCT2020_DECLASS_REDACTED.pdf.ocr.txt")
    assert scrub.wanted("CIA_Note_-_Venezuela_Machines_Intel_Memo_29JUNE2026_DECLASS_REDACTED.pdf.ocr.txt")


def test_scrub_log_is_json_serializable():
    out, log = scrub.scrub("nothing sensitive here")
    assert json.dumps(log)
    assert out == "nothing sensitive here"


def test_ocr_similarity_whitespace_only_is_identical():
    assert tbv.ocr_similarity("a b\nc d", "ab\ncd") == 1.0


def test_ocr_similarity_small_flip_passes_threshold():
    base = "x" * 3000
    flipped = "y" + base[1:]
    assert tbv.ocr_similarity(base, flipped) >= tbv.OCR_SIM_THRESHOLD


def test_ocr_similarity_large_difference_fails_threshold():
    assert tbv.ocr_similarity("a" * 1000, "b" * 1000) < tbv.OCR_SIM_THRESHOLD


def test_compare_ocr_uses_similarity(tmp_path):
    committed = tmp_path / "doc.pdf.ocr.txt"
    produced = tmp_path / "doc_produced.pdf.ocr.txt"
    committed.write_text("The quick brown fox jumps over the lazy dog " * 50, encoding="utf-8")
    produced.write_text("The quick brown fox jumps  over the lazy dog " * 50, encoding="utf-8")
    results = []
    tbv.compare("ocr", str(committed), str(produced), results)
    assert results[0][1] == "PASS"
