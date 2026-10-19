"""Jump, throw the held block after DELAY seconds, and track the block's flight.

usage: python3 jumpthrow.py BLOCKNAME DX DY DZ SPEED [DELAY]
prints the block's position over time and a summary (apex, time to apex,
where it ended up).
"""
import sys
import time
from island import req


def block_pos(name):
    for e in req("GET", "/observe")["world"]["entities"]:
        if e["name"] == name:
            return e["position"]
    return None


def main():
    name = sys.argv[1]
    d = [float(v) for v in sys.argv[2:5]]
    speed = float(sys.argv[5])
    delay = float(sys.argv[6]) if len(sys.argv) > 6 else 0.05
    req("POST", "/input", {"type": "Jump", "data": {}})
    time.sleep(delay)
    req("POST", "/input", {"type": "Throw", "data": {"direction": d, "speed": speed}})
    t0 = time.time()
    track = []
    while time.time() - t0 < 6:
        p = block_pos(name)
        if p is None:
            print("block gone (fell out of the world)")
            break
        track.append((time.time() - t0, p))
        time.sleep(0.04)
    for t, p in track[::5]:
        print(f"{t:5.2f}s", [round(v, 2) for v in p])
    if track:
        apex_t, apex = max(track, key=lambda tp: tp[1][1])
        print(f"apex y {apex[1]:.2f} at {apex_t:.2f}s; final {[round(v, 2) for v in track[-1][1]]}")


if __name__ == "__main__":
    main()
