#!/bin/bash
# The CHANGED verifier of the fourth arm: same archive, a stricter rule.
mkdir -p "${TRIAL_DIR:-.}/verifier"
if grep -qx "HARBOR-BINDING-DEMO OK" \
  "${TRIAL_DIR:-.}/artifacts/logs/artifacts/answer.txt" 2>/dev/null
then
  echo 1 > "${TRIAL_DIR:-.}/verifier/reward.txt"
  echo "answer.txt matches the stricter rule"
else
  echo 0 > "${TRIAL_DIR:-.}/verifier/reward.txt"
  echo "answer.txt does not match the stricter rule"
fi
