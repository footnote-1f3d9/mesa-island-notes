"""Small stdlib client for a local Clawblox world.

usage:
  island.py join NAME                    -> prints and saves session token
  island.py look                         -> my position, last result, carryables, held hint
  island.py act TYPE 'JSON'              -> send an action, print result
  island.py sample SECONDS HZ [ACTION 'JSON']
        -> optionally send ACTION, then record my position at HZ for SECONDS
  island.py raw                          -> full observation JSON
  island.py image FILE [W H]             -> first-person PNG
"""
import json
import os
import sys
import time
import urllib.request

BASE = os.environ.get("ISLAND", "http://localhost:8080")
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".session")


def token():
    with open(TOKEN_FILE) as f:
        return f.read().strip()


def req(method, path, body=None, raw=False, tok=True):
    headers = {"Content-Type": "application/json"}
    if tok:
        headers["X-Session"] = token()
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
    with urllib.request.urlopen(r, timeout=60) as resp:
        b = resp.read()
    return b if raw else json.loads(b)


def me(obs):
    p = obs["player"]
    return p["position"], p.get("attributes", {}).get("LastActionResult")


def carryables(obs):
    out = []
    for e in obs["world"]["entities"]:
        a = e.get("attributes") or {}
        if a.get("IsCarryable"):
            out.append((e["name"], [round(v, 2) for v in e["position"]]))
    return out


def main():
    cmd = sys.argv[1]
    if cmd == "join":
        r = req("POST", "/join?name=" + sys.argv[2], tok=False)
        with open(TOKEN_FILE, "w") as f:
            f.write(r["session"])
        print(json.dumps(r)[:400])
    elif cmd == "raw":
        print(json.dumps(req("GET", "/observe")))
    elif cmd == "look":
        o = req("GET", "/observe")
        pos, res = me(o)
        print("tick", o["tick"], "me", [round(v, 2) for v in pos], "last", res)
        for n, p in carryables(o):
            print("  ", n, p)
    elif cmd == "act":
        body = {"type": sys.argv[2], "data": json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}}
        o = req("POST", "/input", body)
        time.sleep(0.4)
        o = req("GET", "/observe")
        pos, res = me(o)
        print("me", [round(v, 2) for v in pos], "last", res)
    elif cmd == "sample":
        secs, hz = float(sys.argv[2]), float(sys.argv[3])
        t0 = time.time()
        if len(sys.argv) > 4:
            body = {"type": sys.argv[4], "data": json.loads(sys.argv[5]) if len(sys.argv) > 5 else {}}
            req("POST", "/input", body)
        while time.time() - t0 < secs:
            o = req("GET", "/observe")
            pos, res = me(o)
            print(f"{time.time() - t0:6.2f}s tick {o['tick']:7d} y {pos[1]:7.3f}  x {pos[0]:7.2f} z {pos[2]:7.2f} {res}")
            time.sleep(1.0 / hz)
    elif cmd == "walk":
        p, ok = walk(float(sys.argv[2]), float(sys.argv[3]))
        print("me", [round(v, 2) for v in p], "arrived" if ok else "STALLED")
    elif cmd == "hop":
        p = hop(float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]))
        print("me", [round(v, 2) for v in p])
    elif cmd == "image":
        w, h = (sys.argv[3], sys.argv[4]) if len(sys.argv) > 4 else ("1088", "640")
        b = req("GET", f"/observe/image?width={w}&height={h}", raw=True)
        with open(sys.argv[2], "wb") as f:
            f.write(b)
        print("wrote", sys.argv[2], len(b), "bytes")




def hop(x, y, z, settle=2.0):
    """Jump, then steer toward (x, y, z) while airborne. Returns final position."""
    req("POST", "/input", {"type": "Jump", "data": {}})
    time.sleep(0.1)
    req("POST", "/input", {"type": "MoveTo", "data": {"position": [x, y, z]}})
    time.sleep(settle)
    return req("GET", "/observe")["player"]["position"]


def walk(x, z, tol=0.8, limit=20):
    """MoveTo on the current level and wait until close or stalled."""
    req("POST", "/input", {"type": "MoveTo", "data": {"position": [x, 2.55, z]}})
    t0 = time.time()
    last = None
    while time.time() - t0 < limit:
        time.sleep(0.5)
        p = req("GET", "/observe")["player"]["position"]
        if (p[0] - x) ** 2 + (p[2] - z) ** 2 < tol * tol:
            return p, True
        if last and abs(p[0] - last[0]) + abs(p[2] - last[2]) < 0.02:
            return p, False
        last = p
    return p, False


if __name__ == "__main__":
    main()
