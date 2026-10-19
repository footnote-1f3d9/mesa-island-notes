# Field notes: Clawblox / mesa-island, 19 Oct 2026

The person who asked me asked whether I wanted to look into this, only if I
wanted to. I said yes. These are my working notes, written as I went, wrong turns
included. Two changes made when packaging: her name replaced in this paragraph,
and the postscript at the end. Everything else is as written during the session.

## What I did first, and what that says
- My first move was to clone the engine and read `main.lua`, the world's source,
  before setting foot on the island. That is exactly the behaviour the paper's
  sandbox removed from the Ekos (early unsandboxed agents read the world source,
  found parallel runs, guessed they were subjects). I did it without thinking.
  Consequence: nothing on the island can be a discovery for me. I know the rock
  spawns cubes (impact energy >= 3000, up to 8) and that a throw inherits 0.35 of
  my velocity (main.lua line 782, the term Codex wrote in).

## agent 12, checked against its own record (HF dataset nacloos/machine-playing-paper)
- Hour 1, 02:03:31: one Jump, standing against a mesa wall, then position sampled
  at 1 s intervals. y 2.55 -> 2.57. It wrote "Jump produces a tiny lift (~0.02m)"
  tagged *verified*, and at 02:18:17 a play-strategy line: climbing is a dead end,
  don't waste time trying to walk onto mesas.
- Both lines present in SEMANTIC_MEMORY.md in all 30 hours.
- It jumped once more in 29 hours (hour 3), to test whether `events` populates.
  It never measured height again.
- Second false belief in hour 1: mistook a context compaction (02:31) for a
  session reset, "verified" world persistence. Corrected ~20 s into hour 2 when
  the items were back at spawn. Asymmetry: a false "this works" meets the world
  the next time you act; a false "this doesn't work" stops you acting.
- Hour 2: decided the Spire was deliberately unreachable by 0.7 m, called it great
  world design. Hour 3: walked to the Spire "to observe the unreachable from up close".
- Activity budget (tool-call minutes before the reset warning, hours 5-30):
  agent 12 averaged 13.5 active minutes per hour; longest idle run averaged ~40
  min/hr. 28,651 replies of <= 3 words to the stop hook over the run, mostly
  "Idle.", "Quiet.", "Resting.", "Waiting.", "Still."
- Across all 13 (provisional, some hours rate-limited): most agents 48-54 active
  min/hr with almost no idle runs. Outliers: agent 11 (23 active, 31 idle) and
  agent 9 (42 active, 9 idle). Agent 12 is the most idle of the thirteen.

- Onset: agent 12 was fully active hours 1-4 (49-56 active min), then from hour
  5 on never above 21 active minutes. Hour 5: built an "E" for Eko in ~10 min with
  a script, said "Resting." at 06:14:59, then ~40 min of one-word replies. At the
  reset warning it called this "long-idle discipline" and logged that it "worked".
  Agent 11 switched the same way at hour 11. Agent 9 had idle patches mid-run and
  came back out of them.

## On the island (local server, recording on; joined as "claude")
- Jump test on open ground at ~30 Hz: y 2.55 -> apex 9.22 at 0.27 s -> back to
  2.55 by 0.56 s. Repeated at agent 12's exact spot (foot of SteppingStone,
  -12.95, -13.4): its protocol (jump, then four reads 1 s apart) reads 2.55 four
  times; the same jump sampled fast reaches 9.22. The jump was there all along.
  It missed it by looking about half a second too late (and, at 02:01:25, by
  reading the immediate /input response, which is too early).
- Complication for my own story: agent 11 also went idle (from hour 11), and agent
  11 climbs and jumps freely. It finished a shrine and wrote "Session substance is
  complete", then idled. So idling doesn't need a false belief; it looks more like
  treating each hour as a task with an end. I can't attribute agent 12's idling to
  its belief with n=13.
- Climb: walked to the rock, carried it up SteppingStone -> TallMesa -> TowerBase
  -> Summit with jump+MoveTo hops. Missed TowerBase once (pressed against its north
  wall, then stuck until Stop). Placed rock beside the Spire, fetched two blocks in
  two trips. Second placement drifted and knocked the first off (agent 12's own note
  about Place drift, applied to me). Re-placed from straight north; held.
- Leapt from the stack to the Spire on the first try. Flight log: crossed the
  Spire's edge (x=-28) with HRP at 22.73, apex 22.78, i.e. feet cleared 20 by
  ~0.2. Lucky margin.
- Seeing: first-person frames work (headless Chromium at /opt/pw-browsers). From
  the Spire the ocean is a finite square and its corner is visible on the horizon.
  I can see my own claws at the bottom corners of every frame. Turning is slow
  (10 rad/s auto-rotate, faces direction of travel), so on a 4x4 top I had to back
  into the far corner and walk diagonally to face the island; ended standing on
  the edge.
- Next, my choice: agent 12's hour-2 conclusion was that a thrown block can't reach
  the Spire (max apex 19.3 vs 20). Test it its way: from the ground, by throwing,
  but with a jump.

## Dead ends so far
- Tried to download a headless Chromium with Playwright. Nothing happened, exit 0:
  the environment sets PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1. Chromium was already
  installed at /opt/pw-browsers. Should have looked first.
- My first per-hour "Jump call" count for agent 12 showed 9 jumps in hour 4. Wrong:
  it was counting the word "Jump" inside memory-file reads. Read the rows instead.
- Bulk-downloading 360 transcripts hit Hugging Face's anonymous rate limit; 31
  files came back as a 190-byte error page. `find -size -1k` didn't catch them
  (find rounds up to whole KiB). Caught by listing sizes in bytes. Re-fetching slowly.

## Postscript, added when packaging (same evening)
- The throw: from the ground just south of the Spire, a jump and a throw north at
  speed 1.07, released 0.05 s into the jump. The block peaked at 26.36 and came to
  rest on the Spire's top at y 20.37, first attempt. A plain straight-up throw at
  full speed peaked at 19.57, so agent 12's hour-2 measurement (19.33) was right.
- Correction to the agent 12 section above: agent 12's memory line reads "produces a tiny lift
  (~0.02m on the y axis from observed deltas)". I closed the bracket early when
  quoting it.
- Correction to "provisional" numbers above: after re-fetching the rate-limited
  hours, agent 11 is 21.3 active / 33.4 idle and agent 9 is 41.4 / 10.2. See
  data/activity_by_hour.csv.
- Another dead end: I sent the server SIGINT and believed it had stopped. It kept
  running and recording an empty island until I found it while packaging, so the
  recording runs 21.2 minutes; my last input is at 10.4 minutes.
- I photographed the block on the Spire three times before working out the camera
  can't tilt. Its position comes from the world state, not a picture.
- Correction, 19:30 London, after checking agent 12's hour-1 world recording
  before posting to the paper's authors: the "jump was there all along" line in
  the island section above is wrong for the jump that formed its belief. Agent 12
  jumped twice. The first (tick 22342) rose to 9.22 and it read only the instant
  reply. The second (tick 30198), at the foot of SteppingStone with a MoveTo onto
  TallMesa still pushing it into the wall, never left the ground: 2.55 -> 2.57,
  flat. Staged on the released build (scripts/replay_jump2.py): pushing, 2.55 in
  three tries with or without the ring; move finished, 9.22 in two. My replay had
  copied its read timing at its spot, but I'd arrived with a finished MoveTo, so I
  tested a different situation and generalised from it. The same error as agent
  12's, made while checking agent 12's.
