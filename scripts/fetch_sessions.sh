#!/bin/bash
# Fetch session.jsonl for every hour of the given Claude agents from the paper's
# public dataset (huggingface.co/datasets/nacloos/machine-playing-paper).
#
#   DATA=./data-raw scripts/fetch_sessions.sh 01 02 ... 13
#
# One file at a time with a pause. My first version fetched 30 at once and hit
# Hugging Face's anonymous rate limit: 31 files came back as a ~190-byte error
# page that looked like a file. Sizes are checked in bytes here for that reason
# (`find -size -1k` rounds up to whole KiB and misses them).
set -u
DATA=${DATA:-./data-raw}
H=https://huggingface.co/datasets/nacloos/machine-playing-paper/resolve/main/claude_13agents
for a in "$@"; do
  for h in $(seq -w 1 30); do
    d=$DATA/agent$a/hour_$h; mkdir -p "$d"; f=$d/session.jsonl
    if [ -f "$f" ] && [ "$(stat -c %s "$f")" -gt 2000 ]; then continue; fi
    for try in 1 2 3 4; do
      curl -sSL -m 180 "$H/agent$a/hour_$h/session.jsonl" -o "$f"
      [ "$(stat -c %s "$f")" -gt 2000 ] && break
      sleep $((try * 20))
    done
    [ "$(stat -c %s "$f")" -gt 2000 ] || echo "FAILED agent$a hour_$h ($(stat -c %s "$f") bytes)"
    sleep 1
  done
  echo "agent$a done"
done
