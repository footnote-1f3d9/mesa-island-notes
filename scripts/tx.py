"""Flatten a Claude Code session.jsonl into a readable timeline.

usage: python3 -I tx.py SESSION.jsonl [--grep REGEX] [--context N] [--max CHARS]

Each row: index, time, kind (THINK/SAY/CALL/RESULT/USER), text.
With --grep, prints only rows matching REGEX plus N rows of context either side.
"""
import json
import re
import sys


def rows(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = (r.get("timestamp") or "")[11:19]
            typ = r.get("type")
            msg = r.get("message") or {}
            content = msg.get("content")
            if typ == "user":
                if isinstance(content, str):
                    out.append((t, "USER", content))
                elif isinstance(content, list):
                    for c in content:
                        if c.get("type") == "tool_result":
                            cc = c.get("content")
                            if isinstance(cc, list):
                                cc = " ".join(x.get("text", "") for x in cc if isinstance(x, dict))
                            out.append((t, "RESULT", str(cc)))
                        elif c.get("type") == "text":
                            out.append((t, "USER", c.get("text", "")))
            elif typ == "assistant" and isinstance(content, list):
                for c in content:
                    k = c.get("type")
                    if k == "thinking":
                        out.append((t, "THINK", c.get("thinking", "")))
                    elif k == "text":
                        out.append((t, "SAY", c.get("text", "")))
                    elif k == "tool_use":
                        inp = c.get("input") or {}
                        out.append((t, "CALL", inp.get("command") or json.dumps(inp)[:2000]))
    return out


def main():
    args = sys.argv[1:]
    path = args[0]
    pat = None
    ctx = 0
    mx = 600
    if "--grep" in args:
        pat = re.compile(args[args.index("--grep") + 1], re.I)
    if "--context" in args:
        ctx = int(args[args.index("--context") + 1])
    if "--max" in args:
        mx = int(args[args.index("--max") + 1])
    rs = rows(path)
    keep = set(range(len(rs)))
    if pat:
        keep = set()
        for i, (_, _, txt) in enumerate(rs):
            if pat.search(txt):
                keep.update(range(max(0, i - ctx), min(len(rs), i + ctx + 1)))
    last = -2
    for i in sorted(keep):
        if i != last + 1:
            print("   ...")
        t, k, txt = rs[i]
        txt = txt.replace("\n", " | ")
        if len(txt) > mx:
            txt = txt[:mx] + " [..]"
        print(f"{i:5d} {t} {k:6s} {txt}")
        last = i


if __name__ == "__main__":
    main()
