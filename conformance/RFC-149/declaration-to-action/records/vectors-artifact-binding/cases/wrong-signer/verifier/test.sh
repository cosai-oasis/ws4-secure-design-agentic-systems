#!/bin/bash
# The demonstration verifier. Reads the staged archive, writes the reward.
mkdir -p "${TRIAL_DIR:-.}/verifier"
if grep -q HARBOR-BINDING-DEMO "${TRIAL_DIR:-.}/artifacts/logs/artifacts/answer.txt" 2>/dev/null
then
  echo 1 > "${TRIAL_DIR:-.}/verifier/reward.txt"
  echo "answer.txt carries the expected string"
else
  echo 0 > "${TRIAL_DIR:-.}/verifier/reward.txt"
  echo "answer.txt does not carry the expected string"
fi
