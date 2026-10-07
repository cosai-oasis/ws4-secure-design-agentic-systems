"""Recompute the hash chain, the index bookkeeping, the assurance-boundary digest and the checkpoint signature of the sample record."""
import base64, hashlib, json, sys
import rfc8785
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

def digest(obj):
    return "sha256:" + hashlib.sha256(rfc8785.dumps(obj)).hexdigest()

doc = json.load(open(sys.argv[1]))
entries = doc["entries"]
boundary = entries[0]["assurance_boundary"]
assert boundary["statement_digest"] == digest(boundary["statement"]), "assurance-boundary statement digest"
prev = ""
for position, e in enumerate(entries):
    assert e["index"] == position, ("index is not the position", e["index"], position)
    assert e["prev_hash"] == prev, ("prev_hash", position)
    assert e["entry_hash"] == digest({k: v for k, v in e.items() if k != "entry_hash"}), ("entry_hash", position)
    prev = e["entry_hash"]
cp = dict(doc["sequence"]["checkpoint"]); sig = cp.pop("signature")
assert cp["sequence_id"] == doc["sequence"]["id"], "checkpoint names another sequence"
assert cp["expected_boundaries"] == {"first_index": entries[0]["index"], "last_index": entries[-1]["index"]}, "checkpoint boundaries"
assert cp["index"] == entries[-1]["index"] and cp["entry_hash"] == prev, "checkpoint head"
pk = Ed25519PublicKey.from_public_bytes(base64.urlsafe_b64decode(sig["signer"]["x"] + "=="))
pk.verify(base64.urlsafe_b64decode(sig["value"] + "=="), rfc8785.dumps(cp))
print(f"chain ok: {len(entries)} entries, indices 0..{entries[-1]['index']}; boundary statement digest ok; checkpoint signature ok")
