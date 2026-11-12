#!/usr/bin/env python3
"""Prove that verify_all.py / wrapper_gate.py actually catch drift (not just pass on a good repo).

    python3 extraction/prove_drift.py

For each case: copy design-repo/ (plus the cited sibling source files when present) into a
fresh OS temp dir, inject one defect, run verify_all.py there, and require exit 1 with the
named check marked FAIL. A control copy with no defect must pass. Standard library only.
"""
import json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJ = ROOT.parent
HAS_SRC = (PROJ / "src").is_dir()

def fresh():
    tmp = Path(tempfile.mkdtemp(prefix="dr-drift-"))
    shutil.copytree(ROOT, tmp / "design-repo", ignore=shutil.ignore_patterns("__pycache__", "*.zip"))
    if HAS_SRC:
        shutil.copytree(PROJ / "src", tmp / "src")
        for f in ("package.json", "index.html"): shutil.copy(PROJ / f, tmp / f)
    return tmp, tmp / "design-repo"

def jedit(path, fn):
    d = json.loads(path.read_text()); fn(d); path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
def tedit(path, a, b):
    t = path.read_text(); assert a in t, (path, a); path.write_text(t.replace(a, b, 1))

def run(dr, script="extraction/verify_all.py"):
    p = subprocess.run([sys.executable, str(dr / script)], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr

def first_inflow(d, route):
    return next(s for s in d["sectionHeights"]["routes"][route]["sections"] if s["flow"] == "in-flow" and not s["id"].startswith("shell."))

CASE = "/case/espn-who-can-break-calvins-record/"
CASES = [
  ("phantom allowlist entry", "allowlist parity", lambda dr: jedit(dr / "tokens/llm/component-allowlist.json", lambda d: d["primitives"].append("button.ghost"))),
  ("orphan section contract", "allowlist parity", lambda dr: shutil.copy(dr / "sections/media.image.json", dr / "sections/media.gallery.json")),
  ("manifest count drift", "manifest counts recomputed", lambda dr: jedit(dr / "registry.manifest.json", lambda d: d["counts"].update(routes=12))),
  ("allowlistVersion drift", "version parity", lambda dr: jedit(dr / "registry.manifest.json", lambda d: d.update(allowlistVersion="9.9.9"))),
  ("registry loosens a blocked role", "asset availability pinned", lambda dr: jedit(dr / "assets/asset-roles.json", lambda d: d["roles"]["client.logo"].update(availability="generation-safe"))),
  ("pin removed from verify_all code", "asset availability pinned", lambda dr: tedit(dr / "extraction/verify_all.py", '"client.logo": "blocked-for-generation", ', "")),
  ("pin removed from validator code", "asset availability pinned", lambda dr: tedit(dr / "schema/semantic_validate.py", '"client.logo": "blocked-for-generation", ', "")),
  ("contract+allowlist flipped eligible together", "retrievalEligible pinned", lambda dr: (jedit(dr / "sections/utility.back-button.json", lambda d: d.update(retrievalEligible=True)), jedit(dr / "tokens/llm/component-allowlist.json", lambda d: d["sections"]["utility.back-button"].update(retrievalEligible=True)))),
  ("content section marked ineligible", "retrievalEligible pinned", lambda dr: (jedit(dr / "sections/content.media-text.json", lambda d: d.update(retrievalEligible=False, retrievalReason="x" * 40)), jedit(dr / "tokens/llm/component-allowlist.json", lambda d: d["sections"]["content.media-text"].update(retrievalEligible=False)))),
  ("token catalog value drift", "token catalog + policy", lambda dr: jedit(dr / "tokens/llm/token-catalog.json", lambda d: d["color"].update({"color.brand.yellow": "#FFD700"}))),
  ("policy category not a catalog key", "token catalog + policy", lambda dr: jedit(dr / "tokens/llm/token-policy.json", lambda d: d["rawValueRestrictions"].update(typography="x"))),
  ("graph rule edited (policy hash)", "design policy hash", lambda dr: jedit(dr / "compatibility/graph.json", lambda d: d["rules"][0].update(rule=d["rules"][0]["rule"] + " (edited)"))),
  ("graph rule with no validator", "graph rules == validator rules", lambda dr: jedit(dr / "compatibility/graph.json", lambda d: d["rules"].append({"id": "NO_ADJACENT_IMAGES", "severity": "error", "rule": "x"}))),
  ("missing height measurement", "wrapper gate", lambda dr: jedit(dr / "extraction/measured-values.json", lambda d: d["sectionHeights"]["routes"].pop(CASE))),
  ("heights at wrong viewport", "wrapper gate", lambda dr: jedit(dr / "extraction/measured-values.json", lambda d: d["sectionHeights"].update(viewport=1280))),
  ("HERO 3100px", "wrapper gate", lambda dr: jedit(dr / "extraction/measured-values.json", lambda d: next(s for s in d["sectionHeights"]["routes"][CASE]["sections"] if s["id"] == "hero.case").update(height=3100))),
  ("one section holds 70% of page", "wrapper gate", lambda dr: jedit(dr / "extraction/measured-values.json", lambda d: first_inflow(d, CASE).update(height=int(d["sectionHeights"]["routes"][CASE]["pageHeight"] * 0.7)))),
  ("whitelist entry without justification", "wrapper gate", lambda dr: jedit(dr / "extraction/wrapper-whitelist.json", lambda d: d["entries"].append({"route": CASE, "section": "hero.case", "reviewedBy": "jane", "justification": "short", "maxHeightPx": 5000}))),
  ("README count drift", "README counts match disk", lambda dr: tedit(dr / "README.md", "| routes | 11 |", "| routes | 12 |")),
  ("entryPoint outside package", "entryPoints exist inside package", lambda dr: jedit(dr / "registry.manifest.json", lambda d: d["entryPoints"].update(ia="../ia.json"))),
  ("absolute machine path", "no absolute machine paths", lambda dr: tedit(dr / "README.md", "# ", "# " + "/" + "Users" + "/someone/ ")),
  ("copy index stale", "source-copy index covers", lambda dr: jedit(dr / "extraction/source-copy-index.json", lambda d: d.update(fullStrings=d["fullStrings"][:10]))),
  ("generated example leaks brand", "semantic validation", lambda dr: jedit(dr / "schema/examples/generated.home.pagespec.json", lambda d: d["nodes"][0]["content"].update(ownerName="David Lubofsky"))),
]
if HAS_SRC:
    CASES += [
      ("citation out of range", "citations resolve", lambda dr: jedit(dr / "sections/hero.case.json", lambda d: d["source"].update(lines="9000-9010"))),
      ("citation in range, wrong code", "citations resolve", lambda dr: jedit(dr / "sections/hero.case.json", lambda d: d["source"].update(lines="1-5"))),
      ("invented identity pattern", "identity patterns occur", lambda dr: jedit(dr / "extraction/measured-values.json", lambda d: d["sourceIdentity"]["patterns"]["brand"].append("Megatron"))),
    ]

fails = 0
tmp, dr = fresh(); code, out = run(dr)
print(f"{'ok  ' if code == 0 else 'FAIL'} control (unmodified copy) exits {code}"); fails += code != 0
shutil.rmtree(tmp)
for name, check, fn in CASES:
    tmp, dr = fresh(); fn(dr); code, out = run(dr)
    hit = code == 1 and any(l.startswith("FAIL") and check in l for l in out.splitlines())
    fails += not hit
    print(f"{'ok  ' if hit else 'MISS'} {name:46s} -> FAIL '{check}'" + ("" if hit else f"  (exit {code})\n{out[-600:]}"))
    shutil.rmtree(tmp)
# warn-only band: a HERO between 1800 and 3000px must warn, not fail
tmp, dr = fresh()
jedit(dr / "extraction/measured-values.json", lambda d: next(s for s in d["sectionHeights"]["routes"][CASE]["sections"] if s["id"] == "hero.case").update(height=1900))
code, out = run(dr, "extraction/wrapper_gate.py")
hit = code == 0 and "WARN" in out and "1900px > 1800px" in out
fails += not hit
print(f"{'ok  ' if hit else 'MISS'} {'HERO 1900px warns but passes':46s} -> gate exit {code}")
shutil.rmtree(tmp)
print(f"\nprove_drift: {len(CASES) + 2} cases, {fails} failure(s)" + ("" if HAS_SRC else " (citation/identity cases skipped: no sibling source)"))
sys.exit(1 if fails else 0)
