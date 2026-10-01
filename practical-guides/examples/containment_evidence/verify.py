"""Recompute the hash chain and verify the checkpoint signature of the sample record."""
import base64, hashlib, json, sys
import rfc8785
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
doc = json.load(open(sys.argv[1]))
prev = ""
for e in doc["entries"]:
    body = {k: v for k, v in e.items() if k != "entry_hash"}
    h = "sha256:" + hashlib.sha256(rfc8785.dumps(body)).hexdigest()
    assert e["prev_hash"] == prev and e["entry_hash"] == h, e["index"]
    prev = h
cp = dict(doc["sequence"]["checkpoint"]); sig = cp.pop("signature")
assert cp["entry_hash"] == prev
pk = Ed25519PublicKey.from_public_bytes(base64.urlsafe_b64decode(sig["signer"]["x"] + "=="))
pk.verify(base64.urlsafe_b64decode(sig["value"] + "=="), rfc8785.dumps(cp))
print("chain ok:", len(doc["entries"]), "entries; checkpoint signature ok")
