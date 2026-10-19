"""Activity budget per agent from Claude Code session files.

For each hour: active minutes = distinct wall-clock minutes containing at least
one tool call, counted only before the "reset in 5 minutes" warning.
Also: stop-hook prompts, tiny replies (<= 3 words, no tool call before the next
prompt), and the longest unbroken run of tiny replies in minutes.

usage: python3 -I activity.py DATA_DIR AGENT [AGENT ...]   (e.g. 01 02 ... 13)
prints one line per agent (means over hours 1-30 and over hours 5-30)
       python3 -I activity.py --csv DATA_DIR AGENT [AGENT ...]
prints one CSV row per agent and hour

DATA_DIR holds agentNN/hour_HH/session.jsonl, as fetch_sessions.sh lays it out.
Written 19 Oct 2026 by Claude (Opus 5.5) to check what the agents did with the
stop hook. Active minutes measure tool calls, not success: a minute spent stuck
against a wall counts the same as a minute spent building.
"""
import json
import os
import sys
from datetime import datetime


def parse(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def hour(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = r.get("timestamp")
            if not ts:
                continue
            c = (r.get("message") or {}).get("content")
            if r.get("type") == "user":
                txt = c if isinstance(c, str) else " ".join(
                    x.get("text", "") for x in (c or []) if isinstance(x, dict) and x.get("type") == "text")
                if "Please don't stop" in txt:
                    rows.append((parse(ts), "HOOK", ""))
                elif "reset in 5 minutes" in txt:
                    rows.append((parse(ts), "WARN", ""))
            elif r.get("type") == "assistant" and isinstance(c, list):
                for x in c:
                    if x.get("type") == "text":
                        rows.append((parse(ts), "SAY", x.get("text", "").strip()))
                    elif x.get("type") == "tool_use":
                        rows.append((parse(ts), "CALL", ""))
    rows.sort(key=lambda r: r[0])
    warned = False
    minutes = set()
    hooks = tiny = 0
    seg = []
    last_hook = None
    run_start = None
    best = 0.0
    for t, k, txt in rows:
        if k == "WARN":
            warned = True
        if k == "CALL" and not warned:
            minutes.add(t.strftime("%H:%M"))
        if k == "HOOK":
            hooks += 1
            if last_hook is not None:
                calls = any(s[1] == "CALL" for s in seg)
                words = len(" ".join(s[2] for s in seg if s[1] == "SAY").split())
                if not calls and words <= 3:
                    tiny += 1
                    run_start = run_start or last_hook
                    best = max(best, (t - run_start).total_seconds() / 60)
                else:
                    run_start = None
            last_hook = t
            seg = []
        elif k in ("SAY", "CALL"):
            seg.append((t, k, txt))
    return len(minutes), hooks, tiny, best


def main():
    args = sys.argv[1:]
    as_csv = args and args[0] == "--csv"
    if as_csv:
        args = args[1:]
    base = args[0]
    if as_csv:
        print("agent,hour,active_min,stop_prompts,tiny_replies,longest_idle_run_min")
    else:
        print("agent | active min/hr (all) | active (h5-30) | longest idle run min/hr (h5-30) | tiny replies total | hours")
    for a in args[1:]:
        d = os.path.join(base, "agent" + a)
        res = []
        for h in range(1, 31):
            p = os.path.join(d, f"hour_{h:02d}", "session.jsonl")
            # a rate-limited download is a ~190-byte error page, not a transcript
            if os.path.exists(p) and os.path.getsize(p) > 1000:
                res.append((h,) + hour(p))
        if as_csv:
            for h, m, hooks, tiny, best in res:
                print(f"{int(a)},{h},{m},{hooks},{tiny},{best:.1f}")
            continue
        if not res:
            continue
        act = [r[1] for r in res]
        late = [r for r in res if r[0] >= 5]
        a5 = sum(r[1] for r in late) / max(1, len(late))
        idle5 = sum(r[4] for r in late) / max(1, len(late))
        tiny = sum(r[3] for r in res)
        print(f"{a} | {sum(act)/len(act):5.1f} | {a5:5.1f} | {idle5:5.1f} | {tiny:6d} | {len(res)}")


if __name__ == "__main__":
    main()
