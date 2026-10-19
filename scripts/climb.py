"""Climb from open ground east of SteppingStone to the Summit, checking each landing.

The route I worked out by hand on 19 Oct: SteppingStone (top 2.5) -> TallMesa (6)
-> back off TowerBase's north wall -> TowerBase (7) -> Summit (10).
Each step checks the landing height and retries once after a Stop if it missed.
"""
import time
from island import hop, walk, req

STEPS = [
    ("walk", (-5, -10)),
    ("walk", (-11, -12)),
    ("hop", (-17, 5.05, -12), 5.05),
    ("hop", (-22, 8.55, -17), 8.55),
    ("walk", (-27, -18)),
    ("hop", (-27, 9.55, -25), 9.55),
    ("hop", (-27, 12.55, -29.5), 12.55),
]


def main():
    for step in STEPS:
        if step[0] == "walk":
            p, ok = walk(*step[1])
            print("walk", step[1], [round(v, 2) for v in p], "ok" if ok else "STALLED")
            continue
        target, want = step[1], step[2]
        for attempt in (1, 2):
            p = hop(*target)
            good = abs(p[1] - want) < 0.3
            print("hop", target, [round(v, 2) for v in p], "ok" if good else "MISSED")
            if good:
                break
            req("POST", "/input", {"type": "Stop", "data": {}})
            time.sleep(0.5)
        else:
            raise SystemExit("could not make that step")


if __name__ == "__main__":
    main()
