"""Re-stage agent 12's second hour-1 jump (tick 30198 in its recording).

In its recording that jump never left the ground: y went 2.55 -> 2.57 and
stayed. The conditions there: holding Ring_1 overhead, standing at the foot of
SteppingStone's east wall, with a MoveTo onto TallMesa (-25, 8.55, -20) still
active, so the body was pushing into the wall. This stages the same thing on the
released engine, with and without the ring, and with and without the push.

usage (from scripts/, island server running, already joined):
    python3 replay_jump2.py ring push       # agent 12's conditions
    python3 replay_jump2.py noring push
    python3 replay_jump2.py ring nopush     # MoveTo finished first
"""
import sys
import time
from island import req, walk


def me():
    return req("GET", "/observe")["player"]["position"]


def ent(name):
    for e in req("GET", "/observe")["world"]["entities"]:
        if e["name"] == name:
            return e["position"]


def trace_jump(secs=1.2):
    req("POST", "/input", {"type": "Jump", "data": {}})
    t0, peak = time.time(), 0.0
    while time.time() - t0 < secs:
        peak = max(peak, me()[1])
        time.sleep(0.02)
    return peak


def main():
    ring, push = sys.argv[1] == "ring", sys.argv[2] == "push"
    held = ent("Ring_1")
    if ring and held[1] < 3:            # not held yet: fetch it from where it lies
        walk(held[0] - 2, held[2])
        req("POST", "/input", {"type": "Pickup", "data": {"position": held}})
        time.sleep(0.5)
    if not ring and ent("Ring_1")[1] > 3:  # holding it: put it down out of the way
        p = me()
        req("POST", "/input", {"type": "Place", "data": {"position": [p[0] + 3, 0.3, p[2]]}})
        time.sleep(0.8)
    walk(10, 0)
    if push:
        # agent 12's move: aim for TallMesa's top; the body stops against SteppingStone
        req("POST", "/input", {"type": "MoveTo", "data": {"position": [-25, 8.55, -20]}})
        last = None
        for _ in range(60):
            time.sleep(0.5)
            p = me()
            if last and abs(p[0] - last[0]) + abs(p[2] - last[2]) < 0.01:
                break
            last = p
    else:
        walk(-12.95, -13.4)
    p = me()
    print("before jump: pos", [round(v, 2) for v in p], "ring y", round(ent("Ring_1")[1], 2))
    peak = trace_jump()
    print(f"ring={ring} push={push}: peak height {peak:.2f} (standing 2.55)")


if __name__ == "__main__":
    main()
