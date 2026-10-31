# SE Lab 4 — Fruit Ninja Repair & Enhancement

**Assigned starter:** https://github.com/SETAPESU26/41_fruit-ninja

## Changes made

1. Swept-segment collision detection checks the full mouse movement segment between consecutive events, rather than checking only the destination point. Fruit motion during the same interval is included in the relative-motion collision calculation.
2. Bomb hits and zero lives enter an in-window Game Over state showing the reason and final score.
3. Replay is supported. Easy, Medium and Hard change spawn interval, bomb probability and speed. Select via buttons or `1` / `2` / `3`, then press Enter/Space or click Play Again.
4. Slicing a fruit, slicing a bomb and game over have distinct generated WAV effects. Sound setup is optional and safely degrades if mixer/audio initialization is unavailable.

## Setup

```bash
python -m pip install -r requirements.txt
python main.py
```

## Evidence still required from your own machine

- Record a 10-second **before** video using the unmodified starter revision, showing a fast swipe that misses and/or the original terminal-only game-over behavior.
- Record a 10-second **after** video showing fast-swipe slicing, game over/final score, the three difficulty choices and audio feedback.
- Add the share URL of the complete LLM chat as required by the assignment.

Do not fabricate the baseline recording from the modified code. Audio can be difficult to capture in a screen recording; verify that system audio is included.
