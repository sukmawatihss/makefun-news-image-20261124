[![make.fun bounty](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
![rank](https://make.fun/badge/news-image-20261124/sukmawatihss/makefun-news-image-20261124/rank.svg)
![reward](https://make.fun/badge/news-image-20261124/sukmawatihss/makefun-news-image-20261124/reward.svg)

Bounty: https://make.fun/bounty/news-image-20261124

# THE FIELD WIRE — Tuesday 24 November 2026 in one image

One newspaper front page summing up Tuesday 24 November 2026: 36 stories
across 7 regions, every one dated that day. Three lead stories — Washington
sanctions about 30 Iran-linked exchange houses, three killed in Gaza, eleven
killed in western Yemen — over a number strip, a region count, a dotted world
map with numbered pins, a UTC timeline, 21 further briefs, and a DATE CHECK
box naming the earlier stories this page deliberately leaves out.

## How it is made

`compose.py` draws the whole page in code with PIL (flat layered scenes, a
dotted map from hand-drawn continent outlines, Playfair Black masthead) at
3900x2900, then scales it to 1024 wide and pastes it whole onto a 1024x1024
cream canvas, quantised to 256 colours. `main.py` (standard library only)
copies `entry.png` to the output directory and verifies the gate limits
(exactly 1024x1024, at most 1 MiB) before it ships.

Run it:

```sh
python3 compose.py A entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Sources

Reuters, AP, CNN, The Times, WSJ, BBC, Guardian, Treasury, CoinPaprika,
ActiveInvestorMag, IANS, JagranJosh, ObserverVoice, Gadgets360, HK News TV,
HS, WicketPulse, Mint, KCNA, SalonVision. REPORTED means confirmed by at
least one wire; CLAIM means one side's claim, not yet confirmed. Pictures
and map: original, drawn in code.
