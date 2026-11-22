# Action containment example

Code and tests for [Action-Layer Containment for Multimodal Agents](../../multimodal-action-containment.md).

`containment.py` implements the grant check, source labels, exact single-use approvals, a shared budget and a bounded image open. `test_containment.py` runs an allowed case and an attack against each one.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q
```

Expected: `6 passed`. Tested on Python 3.12.10. No network, model or API key is needed.
