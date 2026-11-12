#!/usr/bin/env python3
"""Content hash of the files the design policy is enforced by (BASELINE R15).

    python3 extraction/policy_hash.py           # print sha256:...
    python3 extraction/policy_hash.py --write   # store it in registry.manifest.json + policy/design-policy.json
"""
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENFORCED_BY = ["tokens/llm/token-policy.json", "compatibility/graph.json", "schema/pagespec.schema.json", "schema/semantic_validate.py"]

def compute(root=ROOT):
    h = hashlib.sha256()
    for rel in ENFORCED_BY:
        h.update(rel.encode() + b"\0" + (root / rel).read_bytes() + b"\0")
    return "sha256:" + h.hexdigest()

if __name__ == "__main__":
    v = compute()
    if "--write" in sys.argv:
        for rel, path in (("registry.manifest.json", ("designPolicy",)), ("policy/design-policy.json", ())):
            p = ROOT / rel; d = json.loads(p.read_text())
            tgt = d
            for k in path: tgt = tgt[k]
            tgt["contentHash"] = v
            p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print(v)
