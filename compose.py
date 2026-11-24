#!/usr/bin/env python3
"""THE FIELD WIRE — NI24 entry renderer, Akun 15 (@sukmawatihss).

Original artwork drawn in code with PIL (PIL is the local render tool only —
the shipped entry program main.py is stdlib-only and just copies entry.png).
Layout A: 3 lead cards + 12 minis + dotted world map + timeline + ALSO ON
briefs + DATE CHECK, on a 3900x2900 compose that is scaled to 1024 wide and
pasted whole onto a 1024x1024 cream canvas.

Data layout follows the armada margin-checker conventions so the entry can
be measured: NUMS (number strip), TL (timeline), BRIEFS_L/BRIEFS_R (briefs),
dc (date-check body), PINS (pin table, variant A numbering), grid (the 15
cards as 7-tuples in variant A display order). The CARDS dicts below are the
runtime source for drawing; grid mirrors them for variant A and build()
asserts the two agree.

Usage: python3 compose.py [A|B] [out_png] — variant A is the submitted
design; variant B is the internal duel challenger (different lead order,
different number strip, gold chips instead of red).
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")

# ---------------------------------------------------------------- palette
CREAM = (247, 241, 222)
CREAM_DK = (238, 229, 203)
INK = (28, 34, 28)
GREEN = (30, 77, 43)
GREEN_DK = (17, 46, 26)
GREEN_MID = (56, 110, 70)
GREEN_LT = (216, 230, 205)
RED = (178, 44, 32)
RED_LT = (246, 226, 220)
GOLD = (176, 132, 52)
NAVY = (31, 58, 95)
RUST = (174, 82, 38)
TEAL = (32, 106, 106)
GREY = (110, 110, 105)
WHITE = (255, 255, 255)
SKY = (186, 210, 196)
SAND = (226, 205, 150)

REGION_COLOR = {
    "EUROPE": NAVY,
    "MIDDLE EAST": GREEN,
    "AMERICAS": RUST,
    "OCEANIA": TEAL,
    "WORLD": GREY,
}

W, H = 3900, 2900
M = 60
CW = W - 2 * M  # 3780

_font_cache = {}


def font(name, size):
    key = (name, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(os.path.join(FONTS, name), size)
    return _font_cache[key]


PF = "PlayfairDisplay-Black.ttf"
ARCH = "Archivo-Bold.ttf"
MONO = "IBMPlexMono-Bold.ttf"
MONO_R = "IBMPlexMono-Regular.ttf"
SERIF_B = "DejaVuSerif-Bold.ttf"
SERIF_I = "NotoSerif-Italic.ttf"
SANS_B = "DejaVuSans-Bold.ttf"


def fb(size):
    """Headline font (Archivo Bold)."""
    return font(ARCH, size)


def fr(size):
    """Deck/body font (DejaVu Sans Bold)."""
    return font(SANS_B, size)


def fsr(size):
    """Brief font (DejaVu Sans Bold, small)."""
    return font(SANS_B, size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, max_w):
    words = s.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_tracked(draw, xy, s, f, fill, tracking=10):
    """Draw text with extra space between characters."""
    x, y = xy
    for ch in s:
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + tracking
    return x


def fit_font(draw, s, fname, size, max_w):
    while size > 10 and draw.textlength(s, font=font(fname, size)) > max_w:
        size -= 2
    return font(fname, size)


def rrect(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


# ------------------------------------------------------------------- data
# Cards: key, region, place, headline, deck (<= ~110 chars lead / ~52 mini),
# chip, source, tag, scene kind, map pin (lon, lat) or None.
CARDS = [
    dict(key="iran", region="MIDDLE EAST", place="WASHINGTON",
         headline="US sanctions about 30 Iran-linked exchange houses",
         deck="Treasury names \u224830 houses and executives at the core of shadow banking evading sanctions on Iranian banks.",
         chip="\u224830 SANCTIONED", source="AP \u00b7 TREASURY", tag="REPORTED",
         scene="bank", pin=(-77.03, 38.9)),
    dict(key="gaza", region="MIDDLE EAST", place="GAZA CITY",
         headline="Israeli strikes kill 3 in Gaza",
         deck="Three killed Monday in separate strikes, among them a UNRWA employee. Shifa Hospital confirms.",
         chip="3 KILLED", source="AP", tag="REPORTED",
         scene="city", pin=(34.47, 31.5)),
    dict(key="yemen", region="MIDDLE EAST", place="WESTERN YEMEN",
         headline="Strike kills 11 in western Yemen",
         deck="Houthis say a Saudi-backed forces' strike on Monday killed 11 and wounded 19.",
         chip="11 KILLED \u00b7 19 WOUNDED", source="AP", tag="CLAIM",
         scene="mountains", pin=(43.0, 15.0)),
    dict(key="merkury", region="EUROPE", place="BENGHAZI, LIBYA",
         headline="Ukraine sinks Russian warship Merkury off Libya",
         deck="7 drones launched; Merkury sunk; Angara hit.",
         chip="7 DRONES \u00b7 SUNK", source="CNN \u00b7 TIMES \u00b7 WSJ \u00b7 AP", tag="REPORTED",
         scene="sea", pin=(20.1, 32.1)),
    dict(key="sparta", region="EUROPE", place="GULF OF FINLAND",
         headline="Russian cargo ship Sparta II hit, towed clear",
         deck="Hit by 2 drones; all 16 crew off; towed out Sunday.",
         chip="16 CREW SAFE", source="REUTERS \u00b7 TIMES \u00b7 WSJ", tag="REPORTED",
         scene="sea", pin=(26.2, 60.4)),
    dict(key="kyiv", region="EUROPE", place="KYIV REGION, UKRAINE",
         headline="Russian strikes kill at least 15 near Kyiv",
         deck="15 killed near Kyiv; 11 in Dymer flats.",
         chip="15 KILLED", source="TIMES \u00b7 AP", tag="REPORTED",
         scene="flame", pin=(30.52, 50.45)),
    dict(key="cop31", region="WORLD", place="ANTALYA, T\u00dcRKIYE",
         headline="COP31 ends with no deal \u2014 first since 2000",
         deck="No deal; fossil fuels dropped; talks go to COP32.",
         chip="NO DEAL", source="TIMES \u00b7 GUARDIAN", tag="REPORTED",
         scene="summit", pin=(30.7, 36.9)),
    dict(key="gold", region="AMERICAS", place="MARKETS",
         headline="Gold rebounds 1.5% to $3,588",
         deck="Gold +1.5% after worst week in 8 months.",
         chip="$3,588 \u00b7 +1.5%", source="REUTERS", tag="REPORTED",
         scene="chart", pin=(-74.0, 40.7)),
    dict(key="bitcoin", region="WORLD", place="GLOBAL",
         headline="Bitcoin steadies near $61,284",
         deck="$61,284 at 12:52 UTC; +1.1% in 24h; \u22124.5% in 7d.",
         chip="$61,284", source="COINPAPRIKA", tag="REPORTED",
         scene="chart", pin=None),
    dict(key="gta", region="AMERICAS", place="LOS ANGELES",
         headline="GTA VI takes $3.8bn on day one",
         deck="Biggest entertainment launch on record.",
         chip="$3.8BN", source="ACTIVEINVESTORMAG", tag="REPORTED",
         scene="citynight", pin=(-118.24, 34.05)),
    dict(key="wellington", region="OCEANIA", place="WELLINGTON",
         headline="New Zealand bat out draw with India",
         deck="NZ 239/5: Mitchell 49*, Phillips 26*; India 720/9.",
         chip="DRAW 239/5", source="HS \u00b7 WICKETPULSE", tag="REPORTED",
         scene="cricket", pin=(174.77, -41.28)),
    dict(key="liverpool", region="EUROPE", place="LIVERPOOL",
         headline="Liverpool 4\u20130 Man Utd; Pochettino debut disaster",
         deck="Yoro sent off 8th min; United 19th on 8 points.",
         chip="4\u20130", source="MINT \u00b7 NEXTSPORTSWEB", tag="REPORTED",
         scene="pitch", pin=(-2.99, 53.4)),
    dict(key="trump", region="AMERICAS", place="WASHINGTON",
         headline="Trump: work with Democrats to cap card rates",
         deck="Trump backs cap on card rates; ballot 1 Dec.",
         chip="RATE CAP", source="ACTIVEINVESTORMAG", tag="REPORTED",
         scene="capitol", pin=(-77.03, 38.9)),
    dict(key="democrats", region="AMERICAS", place="WASHINGTON",
         headline="Democrats take both chambers",
         deck="Largest House majority since 1992: 258\u2013173.",
         chip="258\u2013173", source="BBC \u00b7 ACTIVEINVESTORMAG", tag="REPORTED",
         scene="capitol", pin=(-77.03, 38.9)),
    dict(key="nvidia", region="AMERICAS", place="NEW YORK",
         headline="Nvidia brings back Jensen Huang as CEO",
         deck="Huang back as CEO; shares +31%; Nasdaq +6%.",
         chip="+31%", source="REUTERS", tag="REPORTED",
         scene="chart", pin=(-74.0, 40.7)),
]

# grid: (num, region, place, source, headline, deck, scene) in variant A
# display order — mirrors CARDS for variant A (build() asserts this).
grid = [
    (1, "MIDDLE EAST", "WASHINGTON", "AP \u00b7 TREASURY", "US sanctions about 30 Iran-linked exchange houses", "Treasury names \u224830 houses and executives at the core of shadow banking evading sanctions on Iranian banks.", "bank"),
    (2, "MIDDLE EAST", "GAZA CITY", "AP", "Israeli strikes kill 3 in Gaza", "Three killed Monday in separate strikes, among them a UNRWA employee. Shifa Hospital confirms.", "city"),
    (3, "MIDDLE EAST", "WESTERN YEMEN", "AP", "Strike kills 11 in western Yemen", "Houthis say a Saudi-backed forces' strike on Monday killed 11 and wounded 19.", "mountains"),
    (4, "EUROPE", "BENGHAZI, LIBYA", "CNN \u00b7 TIMES \u00b7 WSJ \u00b7 AP", "Ukraine sinks Russian warship Merkury off Libya", "7 drones launched; Merkury sunk; Angara hit.", "sea"),
    (5, "EUROPE", "GULF OF FINLAND", "REUTERS \u00b7 TIMES \u00b7 WSJ", "Russian cargo ship Sparta II hit, towed clear", "Hit by 2 drones; all 16 crew off; towed out Sunday.", "sea"),
    (6, "EUROPE", "KYIV REGION, UKRAINE", "TIMES \u00b7 AP", "Russian strikes kill at least 15 near Kyiv", "15 killed near Kyiv; 11 in Dymer flats.", "flame"),
    (7, "WORLD", "ANTALYA, T\u00dcRKIYE", "TIMES \u00b7 GUARDIAN", "COP31 ends with no deal \u2014 first since 2000", "No deal; fossil fuels dropped; talks go to COP32.", "summit"),
    (8, "AMERICAS", "MARKETS", "REUTERS", "Gold rebounds 1.5% to $3,588", "Gold +1.5% after worst week in 8 months.", "chart"),
    (9, "WORLD", "GLOBAL", "COINPAPRIKA", "Bitcoin steadies near $61,284", "$61,284 at 12:52 UTC; +1.1% in 24h; \u22124.5% in 7d.", "chart"),
    (10, "AMERICAS", "LOS ANGELES", "ACTIVEINVESTORMAG", "GTA VI takes $3.8bn on day one", "Biggest entertainment launch on record.", "citynight"),
    (11, "OCEANIA", "WELLINGTON", "HS \u00b7 WICKETPULSE", "New Zealand bat out draw with India", "NZ 239/5: Mitchell 49*, Phillips 26*; India 720/9.", "cricket"),
    (12, "EUROPE", "LIVERPOOL", "MINT \u00b7 NEXTSPORTSWEB", "Liverpool 4\u20130 Man Utd; Pochettino debut disaster", "Yoro sent off 8th min; United 19th on 8 points.", "pitch"),
    (13, "AMERICAS", "WASHINGTON", "ACTIVEINVESTORMAG", "Trump: work with Democrats to cap card rates", "Trump backs cap on card rates; ballot 1 Dec.", "capitol"),
    (14, "AMERICAS", "WASHINGTON", "BBC \u00b7 ACTIVEINVESTORMAG", "Democrats take both chambers", "Largest House majority since 1992: 258\u2013173.", "capitol"),
    (15, "AMERICAS", "NEW YORK", "REUTERS", "Nvidia brings back Jensen Huang as CEO", "Huang back as CEO; shares +31%; Nasdaq +6%.", "chart"),
]

# PINS: (card number, lon, lat) in variant A numbering. Card 9 (Bitcoin) is
# global and has no single place, so its row carries None coordinates.
PINS = [
    (1, -77.03, 38.9), (2, 34.47, 31.5), (3, 43.0, 15.0), (4, 20.1, 32.1),
    (5, 26.2, 60.4), (6, 30.52, 50.45), (7, 30.7, 36.9), (8, -74.0, 40.7),
    (9, None, None), (10, -118.24, 34.05), (11, 174.77, -41.28),
    (12, -2.99, 53.4), (13, -77.03, 38.9), (14, -77.03, 38.9),
    (15, -74.0, 40.7),
]

NUMS = [
    ("7", "SEA DRONES LAUNCHED"),
    ("\u224830", "IRAN EXCHANGE HOUSES"),
    ("15", "KILLED NEAR KYIV"),
    ("$3,588", "GOLD, +1.5% MONDAY"),
    ("$3.8BN", "GTA VI DAY ONE"),
    ("+31%", "NVIDIA SHARES"),
]
STRIP_B = [
    ("7", "SEA DRONES LAUNCHED"),
    ("44H", "COP31 OVERTIME"),
    ("15", "KILLED NEAR KYIV"),
    ("720/9", "INDIA DECLARED"),
    ("$3.8BN", "GTA VI DAY ONE"),
    ("+31%", "NVIDIA SHARES"),
]

BRIEFS_L = [
    "Nepal PM ends Delhi visit; met Modi (IANS)",
    "UK\u2013EU Brexit reset deal \u2018landmark\u2019 (BBC)",
    "India\u2013EU trade pact likely 16 Dec (JAGRANJOSH)",
    "IFFI 2026 hosts BRICS Roundtable (OBSERVERVOICE)",
    "Modi opens AI Centre at IIT Patna (OBSERVERVOICE)",
    "Amit Shah launches \u20b94,000 cr push (OBSERVERVOICE)",
    "US stocks fall again as AI swings (AP)",
    "KOSPI falls ~3% to 10-month low (REUTERS)",
    "San Francisco AI boom, fears grow (BBC)",
    "N. Korea weighs shutting Swiss office (KCNA)",
    "Congo halts cobalt exports 30 Nov (REUTERS)",
]
BRIEFS_R = [
    "Indonesia: 24 killed in factory blaze (REUTERS)",
    "CrowdStrike buys Zscaler, $44bn (REUTERS)",
    "Thousands march in Lisbon (JAGRANJOSH)",
    "Solana launches solana.ai (GADGETS360)",
    "Miley Cyrus weds Maxx Morando (REUTERS)",
    "UN AI weapons talks continue (SALONVISION)",
    "FBI probes hack of crime database (AP)",
    "Kraken flash crash to ~$17,000 (BITCOINWORLD)",
    "Van Hollen challenges Schumer (ACTIVEINVESTORMAG)",
    "Antalya Pact falls with COP31 text (TIMES)",
]

TL = [
    ("00:02 UTC \u00b7 MON 23 NOV", "UN states agree to keep negotiating lethal AI weapons. (SALONVISION)"),
    ("12:52 UTC \u00b7 MON 23 NOV", "Bitcoin $61,284. (COINPAPRIKA)"),
    ("13:39 UTC \u00b7 MON 23 NOV", "Hong Kong announces Interpol-summit curbs, 30 Nov\u20133 Dec. (HK NEWS TV)"),
    ("MON EVENING UTC", "Treasury sanctions \u224830 Iran exchange houses. (AP)"),
    ("MON EVENING UTC", "Zelenskyy announces the Merkury sinking off Benghazi. (CNN)"),
    ("21:24 UTC MON \u00b7 04:24 WIB TUE", "KCNA: North Korea weighs closing its Swiss office. (REUTERS)"),
]

dc = "186-drone night over Ukraine, 161 downed \u2014 21\u201322 Nov \u00b7 Alcaraz beats Zverev, first ATP Finals title \u2014 22 Nov \u00b7 Verstappen wins the Las Vegas Grand Prix \u2014 22 Nov \u00b7 Wembanyama scores 50, Spurs beat Pelicans \u2014 22 Nov \u00b7 HK Election Committee: 856 cand., 723 seats \u2014 22 Nov \u00b7 Huang resigns as Nvidia CEO after affair \u2014 12 Nov \u00b7 Peru quake itself \u2014 20 Nov (toll count is newer)"
DATECHECK = [s.strip() for s in dc.split("\u00b7")]

# Coarse continent outlines (lon, lat), drawn from general knowledge for
# the dotted map. Equirectangular: lon -180..180, lat 84..-58.
NA = [(-168, 66), (-162, 60), (-156, 58), (-152, 60), (-146, 60), (-140, 60), (-135, 58), (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-110, 24), (-105, 20), (-97, 16), (-94, 17), (-90, 14), (-86, 12), (-83, 9), (-79, 9), (-81, 13), (-84, 16), (-87, 21), (-90, 21), (-91, 19), (-96, 19), (-97, 26), (-93, 30), (-89, 30), (-84, 30), (-81, 25), (-80, 32), (-76, 35), (-74, 40), (-70, 42), (-68, 45), (-65, 44), (-60, 47), (-55, 52), (-60, 55), (-65, 60), (-68, 58), (-78, 62), (-85, 66), (-92, 66), (-95, 69), (-110, 68), (-125, 70), (-140, 70), (-155, 71), (-165, 68)]
GL = [(-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68), (-22, 70), (-20, 74), (-25, 78), (-35, 80), (-50, 80), (-58, 76), (-62, 72)]
SA = [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-70, -50), (-68, -55), (-66, -55), (-65, -45), (-62, -40), (-58, -34), (-52, -32), (-48, -28), (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3), (-44, -2), (-50, 0), (-53, 5), (-58, 6), (-62, 9), (-68, 10), (-72, 12), (-76, 10)]
AF = [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11), (-13, 8), (-8, 5), (-4, 5), (0, 6), (6, 4), (9, 4), (9, -1), (12, -5), (13, -10), (12, -17), (14, -22), (16, -28), (18, -33), (20, -35), (26, -34), (32, -29), (35, -24), (36, -18), (40, -15), (40, -10), (42, -4), (46, -1), (51, 2), (51, 11), (48, 11), (44, 13), (43, 12), (40, 15), (38, 18), (37, 22), (34, 27), (32, 31), (30, 31), (25, 32), (20, 32), (15, 32), (11, 34), (10, 37), (6, 37)]
EUAS = [(-9, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 50), (0, 51), (3, 53), (6, 54), (8, 57), (10, 59), (6, 60), (5, 62), (12, 64), (18, 69), (25, 71), (30, 70), (36, 68), (42, 68), (48, 68), (54, 68), (60, 69), (66, 69), (70, 72), (75, 73), (80, 73), (86, 74), (92, 75), (98, 76), (104, 77), (110, 74), (116, 73), (122, 73), (128, 72), (134, 71), (140, 72), (146, 72), (152, 70), (158, 69), (164, 66), (170, 66), (178, 65), (178, 62), (170, 60), (162, 56), (158, 52), (156, 59), (151, 59), (145, 59), (142, 55), (140, 50), (140, 45), (138, 40), (135, 35), (132, 33), (130, 31), (127, 34), (127, 39), (130, 42), (135, 43), (138, 46), (141, 50), (141, 44), (139, 39), (137, 35), (135, 33), (132, 34), (129, 31), (127, 29), (124, 28), (121, 27), (119, 25), (117, 23), (114, 22), (110, 20), (108, 18), (106, 20), (105, 23), (108, 16), (109, 13), (106, 10), (104, 9), (101, 7), (100, 5), (98, 9), (97, 12), (95, 15), (93, 18), (91, 22), (89, 22), (87, 21), (85, 19), (83, 17), (80, 13), (78, 8), (76, 10), (74, 14), (72, 19), (70, 21), (68, 22), (66, 25), (63, 25), (60, 25), (57, 26), (54, 27), (52, 28), (50, 29), (48, 30), (50, 27), (53, 25), (56, 24), (58, 23), (59, 22), (56, 20), (53, 17), (50, 15), (47, 14), (44, 13), (42, 15), (40, 17), (39, 21), (38, 25), (36, 28), (35, 29), (34, 31), (35, 36), (33, 36), (30, 36), (27, 37), (23, 36), (22, 37), (19, 40), (16, 40), (14, 42), (12, 44), (8, 44), (6, 43), (3, 42), (0, 39), (-2, 37), (-6, 36)]
AU = [(113, -22), (114, -30), (115, -35), (118, -35), (124, -33), (129, -32), (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11), (140, -17), (136, -15), (135, -12), (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51), (-2, 50)]
JP = [(130, 31), (132, 33), (135, 34), (137, 35), (139, 35), (141, 38), (141, 41), (143, 42), (145, 44), (142, 45), (140, 42), (139, 38)]
IDN = [(95, 5), (98, 3), (100, 0), (102, -2), (105, -5), (108, -7), (110, -7), (114, -8), (118, -9), (120, -10), (122, -8), (125, -9), (128, -8), (130, -7), (132, -4), (135, -3), (138, -2), (141, -3), (141, -8), (138, -8), (135, -7), (132, -6), (130, -5), (128, -3), (126, 0), (124, 1), (122, 0), (120, 1), (118, 0), (116, 2), (114, 3), (112, 5), (110, 6), (108, 6), (106, 6), (104, 2), (102, 1), (100, 2), (97, 5)]
NZ = [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38), (178, -37), (175, -36), (173, -35), (170, -40), (167, -44)]
MG = [(44, -16), (47, -15), (50, -16), (50, -20), (48, -24), (45, -25), (43, -22), (43, -18)]
IS = [(-22, 64), (-18, 63), (-14, 64), (-15, 66), (-20, 66), (-24, 65)]
PH = [(120, 18), (121, 16), (122, 14), (124, 11), (126, 7), (127, 6), (126, 8), (124, 10), (122, 13), (121, 16)]
CU = [(-85, 22), (-80, 23), (-75, 20), (-74, 20), (-77, 21), (-82, 22)]
LAND = [NA, GL, SA, AF, EUAS, AU, UK, JP, IDN, NZ, MG, IS, PH, CU]


# ------------------------------------------------------------------ scenes
def scene(draw, box, kind, dark=False):
    """Flat layered scene strip inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    if kind == "bank":
        draw.rectangle(box, fill=GREEN_DK)
        draw.rectangle([x0, y0, x1, y0 + h * 0.45], fill=(44, 96, 58))
        # bank building
        bx0, by0, bx1, by1 = x0 + w * 0.30, y0 + h * 0.30, x0 + w * 0.72, y1 - h * 0.12
        draw.polygon([(bx0 - 12, by0), ((bx0 + bx1) / 2, by0 - h * 0.22), (bx1 + 12, by0)], fill=GOLD)
        draw.rectangle([bx0, by0, bx1, by1], fill=CREAM)
        for i in range(5):
            cx = bx0 + (i + 0.5) * (bx1 - bx0) / 5
            draw.rectangle([cx - 7, by0 + 8, cx + 7, by1 - 6], fill=GREEN_DK)
        draw.rectangle([bx0 - 14, by1, bx1 + 14, by1 + h * 0.10], fill=GOLD)
        for i in range(3):  # coin stacks
            cx = x0 + w * (0.10 + i * 0.07)
            for j in range(3):
                draw.ellipse([cx - 16, y1 - 22 - j * 14, cx + 16, y1 - 6 - j * 14], fill=GOLD, outline=GREEN_DK)
        draw.ellipse([x0 + w * 0.86, y0 + h * 0.12, x0 + w * 0.86 + 44, y0 + h * 0.12 + 44], fill=RED)
    elif kind == "city":
        draw.rectangle(box, fill=(214, 164, 110))
        draw.rectangle([x0, y0 + h * 0.55, x1, y1], fill=(120, 84, 66))
        draw.ellipse([x0 + w * 0.78, y0 + h * 0.08, x0 + w * 0.78 + 52, y0 + h * 0.08 + 52], fill=(240, 200, 90))
        for i, bh in enumerate([0.55, 0.75, 0.62, 0.85, 0.58]):
            bx = x0 + w * (0.06 + i * 0.17)
            bw = w * 0.13
            draw.rectangle([bx, y1 - h * bh, bx + bw, y1], fill=(58, 52, 48))
            for wy in range(3):
                for wx in range(2):
                    draw.rectangle([bx + 8 + wx * 22, y1 - h * bh + 12 + wy * 26, bx + 20 + wx * 22, y1 - h * bh + 24 + wy * 26], fill=(250, 220, 130))
        # minaret
        mx = x0 + w * 0.88
        draw.rectangle([mx, y0 + h * 0.18, mx + 16, y1], fill=(58, 52, 48))
        draw.polygon([(mx - 6, y0 + h * 0.18), (mx + 8, y0 + h * 0.02), (mx + 22, y0 + h * 0.18)], fill=RED)
    elif kind == "mountains":
        draw.rectangle(box, fill=(232, 196, 140))
        draw.ellipse([x0 + w * 0.70, y0 + h * 0.06, x0 + w * 0.70 + 56, y0 + h * 0.06 + 56], fill=(240, 140, 60))
        draw.polygon([(x0, y1), (x0 + w * 0.30, y0 + h * 0.30), (x0 + w * 0.62, y1)], fill=(96, 74, 52))
        draw.polygon([(x0 + w * 0.40, y1), (x0 + w * 0.68, y0 + h * 0.18), (x1, y1)], fill=(70, 52, 38))
        draw.polygon([(x0, y1), (x0 + w * 0.18, y0 + h * 0.55), (x0 + w * 0.42, y1)], fill=(124, 98, 70))
        for i in range(3):
            bx = x0 + w * (0.12 + i * 0.10)
            draw.arc([bx, y0 + h * 0.14, bx + 26, y0 + h * 0.14 + 16], 180, 360, fill=INK, width=4)
    elif kind == "sea":
        draw.rectangle(box, fill=(140, 178, 196))
        draw.rectangle([x0, y0 + h * 0.52, x1, y1], fill=(28, 68, 110))
        draw.ellipse([x0 + w * 0.80, y0 + h * 0.08, x0 + w * 0.80 + 48, y0 + h * 0.08 + 48], fill=(250, 220, 120))
        for i in range(3):
            yy = y0 + h * (0.58 + i * 0.14)
            draw.arc([x0 + 10, yy, x0 + w * 0.35, yy + 26], 180, 360, fill=WHITE, width=5)
            draw.arc([x0 + w * 0.55, yy, x0 + w * 0.90, yy + 26], 180, 360, fill=WHITE, width=5)
        # ship
        sx, sy = x0 + w * 0.30, y0 + h * 0.42
        draw.polygon([(sx, sy + 26), (sx + w * 0.30, sy + 26), (sx + w * 0.26, sy + 52), (sx + 8, sy + 52)], fill=(40, 40, 44))
        draw.rectangle([sx + w * 0.05, sy, sx + w * 0.12, sy + 26], fill=CREAM)
        draw.rectangle([sx + w * 0.14, sy + 8, sx + w * 0.20, sy + 26], fill=RED)
        draw.rectangle([sx + w * 0.21, sy + 8, sx + w * 0.27, sy + 26], fill=GOLD)
        draw.line([sx + w * 0.08, sy, sx + w * 0.08, sy - h * 0.22], fill=INK, width=4)
        for i in range(2):  # drones
            dx, dy = x0 + w * (0.68 + i * 0.10), y0 + h * (0.16 + i * 0.12)
            draw.ellipse([dx - 8, dy - 8, dx + 8, dy + 8], fill=INK)
            draw.line([dx - 16, dy, dx + 16, dy], fill=INK, width=3)
    elif kind == "flame":
        draw.rectangle(box, fill=(52, 40, 36))
        for i, bh in enumerate([0.5, 0.7, 0.6]):
            bx = x0 + w * (0.10 + i * 0.28)
            draw.rectangle([bx, y1 - h * bh, bx + w * 0.20, y1], fill=(24, 22, 20))
        # flames
        for cx, s, col in [(0.35, 1.0, (240, 120, 40)), (0.52, 0.75, (250, 180, 60)), (0.68, 0.9, (240, 120, 40))]:
            fx = x0 + w * cx
            fy = y0 + h * 0.55
            draw.polygon([(fx - 34 * s, fy + 40 * s), (fx - 10 * s, fy - 10 * s), (fx, fy - 62 * s), (fx + 12 * s, fy - 6 * s), (fx + 34 * s, fy + 40 * s)], fill=col)
        for i in range(3):
            draw.ellipse([x0 + w * (0.15 + i * 0.25), y0 + h * 0.08, x0 + w * (0.15 + i * 0.25) + 40, y0 + h * 0.08 + 26], fill=(140, 130, 120))
    elif kind == "summit":
        draw.rectangle(box, fill=GREEN_LT)
        draw.ellipse([x0 + w * 0.44, y0 + h * 0.10, x0 + w * 0.44 + 58, y0 + h * 0.10 + 58], fill=GREEN)
        for i, col in enumerate([NAVY, RED, GOLD, TEAL, RUST]):
            fx = x0 + w * (0.10 + i * 0.18)
            draw.line([fx, y0 + h * 0.30, fx, y1 - h * 0.10], fill=INK, width=4)
            draw.polygon([(fx, y0 + h * 0.30), (fx + 44, y0 + h * 0.38), (fx, y0 + h * 0.46)], fill=col)
        draw.rectangle([x0, y1 - h * 0.10, x1, y1], fill=GREEN_DK)
    elif kind == "chart":
        draw.rectangle(box, fill=CREAM_DK)
        base = y1 - h * 0.18
        for i, bh in enumerate([0.25, 0.35, 0.30, 0.55, 0.70, 0.85]):
            bx = x0 + w * (0.10 + i * 0.14)
            col = GREEN if i < 5 else RED
            draw.rectangle([bx, base - h * bh, bx + w * 0.09, base], fill=col)
        pts = [(x0 + w * (0.10 + i * 0.14) + w * 0.045, base - h * bh) for i, bh in enumerate([0.25, 0.35, 0.30, 0.55, 0.70, 0.85])]
        draw.line(pts, fill=INK, width=4)
        for px, py in pts:
            draw.ellipse([px - 7, py - 7, px + 7, py + 7], fill=WHITE, outline=INK, width=3)
        draw.line([x0 + w * 0.06, base, x1 - w * 0.04, base], fill=INK, width=3)
    elif kind == "citynight":
        draw.rectangle(box, fill=(24, 28, 52))
        for i in range(14):
            sx = x0 + w * (0.04 + (i * 0.067) % 0.92)
            sy = y0 + h * (0.06 + (i * 0.037) % 0.30)
            draw.ellipse([sx, sy, sx + 5, sy + 5], fill=WHITE)
        for i, bh in enumerate([0.55, 0.8, 0.65, 0.9]):
            bx = x0 + w * (0.08 + i * 0.22)
            draw.rectangle([bx, y1 - h * bh, bx + w * 0.16, y1], fill=(52, 58, 92))
            for wy in range(4):
                for wx in range(2):
                    draw.rectangle([bx + 8 + wx * 24, y1 - h * bh + 12 + wy * 24, bx + 20 + wx * 24, y1 - h * bh + 22 + wy * 24], fill=(250, 220, 110))
        draw.rectangle([x0 + w * 0.72, y0 + h * 0.30, x0 + w * 0.92, y0 + h * 0.62], fill=RED)
        draw.text((x0 + w * 0.74, y0 + h * 0.38), "VI", font=font(ARCH, 34), fill=WHITE)
    elif kind == "cricket":
        draw.rectangle(box, fill=(96, 150, 80))
        draw.rectangle([x0 + w * 0.30, y0, x0 + w * 0.70, y1], fill=(210, 190, 140))
        draw.line([x0 + w * 0.30, y0 + h * 0.5, x0 + w * 0.70, y0 + h * 0.5], fill=WHITE, width=3)
        for sx in (0.36, 0.64):
            px = x0 + w * sx
            for k in range(3):
                draw.line([px + k * 8, y0 + h * 0.30, px + k * 8, y0 + h * 0.30 + 26], fill=(250, 220, 120), width=4)
        draw.ellipse([x0 + w * 0.48, y0 + h * 0.62, x0 + w * 0.48 + 18, y0 + h * 0.62 + 18], fill=RED)
        draw.line([x0 + w * 0.78, y0 + h * 0.20, x0 + w * 0.88, y0 + h * 0.55], fill=(120, 84, 50), width=8)
    elif kind == "pitch":
        draw.rectangle(box, fill=(56, 130, 70))
        for i in range(5):
            draw.rectangle([x0 + i * w / 5, y0, x0 + (i + 1) * w / 5, y1], fill=(64, 142, 78) if i % 2 else (56, 130, 70))
        draw.ellipse([x0 + w * 0.42, y0 + h * 0.20, x0 + w * 0.58, y0 + h * 0.80], outline=WHITE, width=4)
        draw.line([x0 + w * 0.50, y0, x0 + w * 0.50, y1], fill=WHITE, width=4)
        draw.ellipse([x0 + w * 0.66, y0 + h * 0.60, x0 + w * 0.66 + 20, y0 + h * 0.60 + 20], fill=WHITE, outline=INK)
        draw.rectangle([x0 + w * 0.06, y0 + h * 0.30, x0 + w * 0.06 + 8, y0 + h * 0.70], fill=WHITE)
    elif kind == "capitol":
        draw.rectangle(box, fill=(200, 214, 226))
        cx = x0 + w * 0.50
        draw.rectangle([cx - w * 0.30, y1 - h * 0.35, cx + w * 0.30, y1 - h * 0.12], fill=WHITE)
        draw.pieslice([cx - w * 0.16, y0 + h * 0.10, cx + w * 0.16, y0 + h * 0.10 + w * 0.32], 180, 360, fill=WHITE)
        draw.rectangle([cx - 4, y0 + h * 0.02, cx + 4, y0 + h * 0.12], fill=INK)
        draw.polygon([(cx + 4, y0 + h * 0.02), (cx + 40, y0 + h * 0.08), (cx + 4, y0 + h * 0.14)], fill=RED)
        for i in range(5):
            colx = cx - w * 0.24 + i * w * 0.12
            draw.rectangle([colx, y1 - h * 0.35, colx + 10, y1 - h * 0.12], fill=NAVY)
        draw.rectangle([x0, y1 - h * 0.12, x1, y1], fill=GREEN_MID)
    else:
        draw.rectangle(box, fill=GREEN_LT)


# ------------------------------------------------------------------- map
def lonlat_to_xy(lon, lat, x0, y0, w, h):
    x = x0 + (lon + 180.0) / 360.0 * w
    y = y0 + (84.0 - lat) / 142.0 * h
    return x, y


def dotted_map(draw, box, pins):
    """Dotted world map from the LAND polygons above, with numbered pins."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    # rasterise land polygons to a small mask, then dot-sample it
    mw, mh = 360, 140
    mask = Image.new("L", (mw, mh), 0)
    md = ImageDraw.Draw(mask)
    for poly in LAND:
        pts = [((lon + 180.0) / 360.0 * mw, (84.0 - lat) / 142.0 * mh) for lon, lat in poly]
        md.polygon(pts, fill=255)
    step = 4
    for my in range(0, mh, step):
        for mx in range(0, mw, step):
            if mask.getpixel((mx, my)):
                px = x0 + mx / mw * w
                py = y0 + my / mh * h
                draw.ellipse([px - 5, py - 5, px + 5, py + 5], fill=GREEN_DK)
    # pins: number = display number of the card
    offs = {}
    for num, (lon, lat) in pins:
        key = (round(lon, 1), round(lat, 1))
        n = offs.get(key, 0)
        offs[key] = n + 1
        dx = (n % 2) * 52 - (26 if n else 0)
        dy = -((n // 2) * 56)
        px, py = lonlat_to_xy(lon, lat, x0, y0, w, h)
        px += dx
        py += dy
        draw.ellipse([px - 27, py - 27, px + 27, py + 27], fill=RED, outline=WHITE, width=4)
        f = font(ARCH, 32)
        tw = draw.textlength(str(num), font=f)
        draw.text((px - tw / 2, py - 21), str(num), font=f, fill=WHITE)


# ------------------------------------------------------------------ cards
def lead(draw, box, card, num, accent):
    x0, y0, x1, y1 = box
    w = x1 - x0
    draw.rectangle(box, fill=WHITE, outline=GREEN_DK, width=3)
    scene(draw, (x0 + 3, y0 + 3, x1 - 3, y0 + 203), card["scene"])
    # number badge on the scene
    draw.ellipse([x0 + 22, y0 + 18, x0 + 86, y0 + 82], fill=GREEN, outline=WHITE, width=4)
    f = font(ARCH, 40)
    tw = draw.textlength(str(num), font=f)
    draw.text((x0 + 54 - tw / 2, y0 + 28), str(num), font=f, fill=WHITE)
    # region + place
    f = font(MONO, 30)
    draw.text((x0 + 24, y0 + 212), "%s \u00b7 %s" % (card["place"], card["region"]), font=f, fill=REGION_COLOR[card["region"]])
    # headline
    f = fb(68)
    lines = wrap(draw, card["headline"], f, w - 48)[:2]
    yy = y0 + 246
    for ln in lines:
        draw.text((x0 + 24, yy), ln, font=f, fill=INK)
        yy += 74
    # deck
    f = fr(38)
    dlines = wrap(draw, card["deck"], f, w - 48)[:2]
    yy = y0 + 400
    for ln in dlines:
        draw.text((x0 + 24, yy), ln, font=f, fill=(64, 70, 64))
        yy += 44
    # chip + tag + source row
    cy = y0 + 492
    f = font(ARCH, 36)
    chip = card["chip"]
    cw = draw.textlength(chip, font=f) + 36
    rrect(draw, [x0 + 24, cy, x0 + 24 + cw, cy + 46], 23, fill=accent)
    draw.text((x0 + 42, cy + 5), chip, font=f, fill=WHITE)
    tag = card["tag"]
    tf = font(MONO, 32)
    tc = RED if tag == "CLAIM" else GREEN
    draw.text((x0 + 24 + cw + 20, cy + 7), tag, font=tf, fill=tc)
    sf = font(MONO_R, 30)
    src = card["source"]
    sw = draw.textlength(src, font=sf)
    draw.text((x1 - 24 - sw, cy + 9), src, font=sf, fill=GREY)


def mini(draw, box, card, num, accent):
    x0, y0, x1, y1 = box
    w = x1 - x0
    rc = REGION_COLOR[card["region"]]
    draw.rectangle(box, fill=WHITE, outline=GREEN_DK, width=2)
    # data band
    draw.rectangle([x0, y0, x1, y0 + 40], fill=rc)
    f = font(MONO, 28)
    draw.text((x0 + 16, y0 + 6), "%d \u00b7 %s \u00b7 %s" % (num, card["place"], card["region"]), font=f, fill=WHITE)
    cf = font(ARCH, 26)
    chip = card["chip"]
    cw = draw.textlength(chip, font=cf)
    draw.text((x1 - 16 - cw, y0 + 7), chip, font=cf, fill=(255, 235, 150))
    # headline
    f = fb(48)
    lines = wrap(draw, card["headline"], f, w - 40)[:2]
    yy = y0 + 48
    for ln in lines:
        draw.text((x0 + 20, yy), ln, font=f, fill=INK)
        yy += 52
    # deck: one terse line, shrunk to fit
    df = fr(34)
    while draw.textlength(card["deck"], font=df) > w - 40 and df.size > 18:
        df = fr(df.size - 1)
    draw.text((x0 + 20, y0 + 158), card["deck"], font=df, fill=(64, 70, 64))
    # source + tag at the bottom
    sf = font(MONO_R, 25)
    draw.text((x0 + 20, y0 + 192), card["source"], font=sf, fill=GREY)
    tf = font(MONO, 25)
    tag = card["tag"]
    tc = RED if tag == "CLAIM" else GREEN
    tw = draw.textlength(tag, font=tf)
    draw.text((x1 - 20 - tw, y0 + 192), tag, font=tf, fill=tc)


# ------------------------------------------------------------------ build
def build(variant):
    accent = RED if variant == "A" else GOLD
    strip = NUMS if variant == "A" else STRIP_B
    lead_keys = ["iran", "gaza", "yemen"] if variant == "A" else ["gaza", "yemen", "iran"]
    by_key = {c["key"]: c for c in CARDS}
    leads = [by_key[k] for k in lead_keys]
    minis = [c for c in CARDS if c["key"] not in lead_keys]
    order = leads + minis
    for i, c in enumerate(order):
        c["num"] = i + 1
    if variant == "A":
        # grid must mirror the drawn cards exactly (headline + deck + scene).
        assert [g[4] for g in grid] == [c["headline"] for c in order], "grid headlines drifted from CARDS"
        assert [g[5] for g in grid] == [c["deck"] for c in order], "grid decks drifted from CARDS"
        assert [g[6] for g in grid] == [c["scene"] for c in order], "grid scenes drifted from CARDS"
    region_counts = {}
    for c in order:
        region_counts[c["region"]] = region_counts.get(c["region"], 0) + 1

    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    # kicker
    kicker = "36 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED TUESDAY 24 NOVEMBER 2026"
    kf = font(ARCH, 44)
    total_w = sum(draw.textlength(ch, font=kf) + 8 for ch in kicker) - 8
    draw_tracked(draw, ((W - total_w) / 2, 48), kicker, kf, GREEN_DK, tracking=8)
    draw.line([M, 108, W - M, 108], fill=GREEN_DK, width=4)

    # masthead
    mf = font(PF, 250)
    name = "THE FIELD WIRE"
    tw = draw.textlength(name, font=mf)
    draw.text(((W - tw) / 2, 110), name, font=mf, fill=GREEN_DK)
    draw.line([M, 378, W - M, 378], fill=GREEN_DK, width=3)

    # date line
    df = font(PF, 108)
    date = "Tuesday 24 November 2026"
    tw = draw.textlength(date, font=df)
    draw.text(((W - tw) / 2, 382), date, font=df, fill=GREEN)
    draw.line([M, 432, M + 260, 432], fill=GREEN_DK, width=3)
    draw.line([W - M - 260, 432, W - M, 432], fill=GREEN_DK, width=3)

    # deck
    deck = "Washington sanctions Tehran\u2019s shadow banks \u2014 three killed in Gaza \u2014 eleven killed in Yemen."
    sf = font(SERIF_I, 50)
    tw = draw.textlength(deck, font=sf)
    draw.text(((W - tw) / 2, 522), deck, font=sf, fill=RED)

    # number strip
    y = 584
    cell_w = (CW - 5 * 12) / 6
    for i, (big, label) in enumerate(strip):
        cx0 = M + i * (cell_w + 12)
        draw.rectangle([cx0, y, cx0 + cell_w, y + 192], fill=WHITE, outline=GREEN_DK, width=3)
        bf = fit_font(draw, big, ARCH, 96, cell_w - 30)
        bw = draw.textlength(big, font=bf)
        draw.text((cx0 + (cell_w - bw) / 2, y + 18), big, font=bf, fill=GREEN_DK)
        lf = font(MONO, 33)
        lw = draw.textlength(label, font=lf)
        draw.text((cx0 + (cell_w - lw) / 2, y + 132), label, font=lf, fill=INK)
        draw.rectangle([cx0 + cell_w / 2 - 40, y + 178, cx0 + cell_w / 2 + 40, y + 184], fill=accent)

    # region strip
    y = 788
    draw.rectangle([M, y, W - M, y + 68], fill=GREEN_DK)
    rf = font(MONO, 34)
    draw.text((M + 24, y + 16), "THE 15 LEAD STORIES BY REGION", font=rf, fill=CREAM)
    rx = W - M - 24
    for region in ["EUROPE", "MIDDLE EAST", "AMERICAS", "OCEANIA", "WORLD"]:
        label = "%s %d" % (region, region_counts.get(region, 0))
        lf = font(ARCH, 32)
        lw = draw.textlength(label, font=lf)
        rx -= lw + 36
        rrect(draw, [rx, y + 12, rx + lw + 36, y + 56], 22, fill=REGION_COLOR[region], outline=CREAM, width=2)
        draw.text((rx + 18, y + 19), label, font=lf, fill=WHITE)
        rx -= 16

    # lead row
    y = 872
    lead_w = (CW - 2 * 24) / 3
    for i, card in enumerate(leads):
        lx0 = M + i * (lead_w + 24)
        lead(draw, (lx0, y, lx0 + lead_w, y + 540), card, card["num"], accent)

    # mini grid 4 x 3
    y = 1432
    mini_w = (CW - 3 * 20) / 4
    for row in range(3):
        for col in range(4):
            card = minis[row * 4 + col]
            mx0 = M + col * (mini_w + 20)
            mini(draw, (mx0, y + row * 220, mx0 + mini_w, y + row * 220 + 220), card, card["num"], accent)

    # DATE CHECK strip
    y = 2132
    draw.rectangle([M, y, W - M, y + 150], fill=RED_LT, outline=RED, width=4)
    df2 = font(ARCH, 34)
    draw.text((M + 24, y + 8), "DATE CHECK \u2014 NOT TODAY\u2019S NEWS", font=df2, fill=RED)
    note = "These happened earlier. They are not today\u2019s stories."
    nf = font(MONO_R, 28)
    nw = draw.textlength(note, font=nf)
    draw.text((W - M - 24 - nw, y + 12), note, font=nf, fill=RED)
    item_w = (CW - 48) / 4
    for row in range(2):
        for col in range(4):
            idx = row * 4 + col
            if idx >= len(DATECHECK):
                break
            ix = M + 24 + col * item_w
            iy = y + 52 + row * 46
            fitem = fit_font(draw, "\u2022 " + DATECHECK[idx], SANS_B, 26, item_w - 24)
            draw.text((ix, iy), "\u2022 " + DATECHECK[idx], font=fitem, fill=INK)

    # bottom band: map | timeline | ALSO ON
    y = 2302
    col_w = (CW - 2 * 30) / 3
    col_x = [M, M + col_w + 30, M + 2 * (col_w + 30)]
    hf = font(ARCH, 36)

    # map column
    draw.text((col_x[0], y), "WHERE IT HAPPENED", font=hf, fill=GREEN_DK)
    draw.line([col_x[0], y + 48, col_x[0] + col_w, y + 48], fill=GREEN_DK, width=3)
    pins = [(c["num"], c["pin"]) for c in order if c["pin"]]
    dotted_map(draw, (col_x[0], y + 62, col_x[0] + col_w, y + 62 + 380), pins)
    mf2 = font(SANS_B, 26)
    for j, ln in enumerate(wrap(draw, "Dotted map: pins match story numbers. 9 Bitcoin is global \u2014 no single place. Washington holds 1, 13, 14; New York holds 8, 15.", mf2, col_w)):
        draw.text((col_x[0], y + 452 + j * 28), ln, font=mf2, fill=INK)

    # timeline column
    draw.text((col_x[1], y), "THE DAY IN UTC", font=hf, fill=GREEN_DK)
    draw.line([col_x[1], y + 48, col_x[1] + col_w, y + 48], fill=GREEN_DK, width=3)
    tf = font(MONO, 30)
    ty = y + 62
    for label, text in TL:
        draw.text((col_x[1], ty), label, font=tf, fill=RED)
        ftext = fit_font(draw, text, SANS_B, 30, col_w)
        draw.text((col_x[1], ty + 34), text, font=ftext, fill=INK)
        ty += 68
    draw.text((col_x[1], ty + 2), "Hours are as reported; Monday-evening items are labelled as such.", font=font(MONO_R, 26), fill=GREY)

    # ALSO ON column
    draw.text((col_x[2], y), "ALSO ON \u2014 TUESDAY 24 NOVEMBER", font=hf, fill=GREEN_DK)
    draw.line([col_x[2], y + 48, col_x[2] + col_w, y + 48], fill=GREEN_DK, width=3)
    sub_w = (col_w - 20) / 2
    for half_i, half_list in enumerate((BRIEFS_L, BRIEFS_R)):
        bx = col_x[2] + half_i * (sub_w + 20)
        for j, brief in enumerate(half_list):
            num = 16 + (len(BRIEFS_L) if half_i else 0) + j
            txt = "%d %s" % (num, brief)
            fbrief = fsr(25)
            while draw.textlength(txt, font=fbrief) > sub_w and fbrief.size > 18:
                fbrief = fsr(fbrief.size - 1)
            draw.text((bx, y + 62 + j * 40), txt, font=fbrief, fill=INK)

    # footer
    fy = 2820
    draw.line([M, fy - 8, W - M, fy - 8], fill=GREEN_DK, width=3)
    ff = font(MONO_R, 29)
    line1 = "SOURCES: REUTERS \u00b7 AP \u00b7 CNN \u00b7 THE TIMES \u00b7 WSJ \u00b7 BBC \u00b7 GUARDIAN \u00b7 TREASURY \u00b7 COINPAPRIKA \u00b7 ACTIVEINVESTORMAG \u00b7 IANS \u00b7 JAGRANJOSH \u00b7 OBSERVERVOICE \u00b7 GADGETS360 \u00b7 HK NEWS TV \u00b7 HS \u00b7 WICKETPULSE \u00b7 MINT \u00b7 KCNA \u00b7 SALONVISION"
    draw.text((M, fy), line1, font=ff, fill=INK)
    line2 = "REPORTED = confirmed by at least one wire \u00b7 CLAIM = one side\u2019s claim, not yet confirmed \u00b7 Pictures and map: original, drawn in code."
    draw.text((M, fy + 36), line2, font=ff, fill=INK)
    return img


def finalize(compose_img, out_path):
    """Scale the wide compose to 1024 wide, paste whole onto a 1024x1024
    cream canvas, quantise to 256 colours (G6 method)."""
    scaled = compose_img.resize((1024, int(1024 * H / W)), Image.LANCZOS)
    canvas = Image.new("RGB", (1024, 1024), CREAM)
    canvas.paste(scaled, (0, (1024 - scaled.height) // 2))
    out = canvas.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    out.save(out_path, format="PNG", optimize=True)
    return out_path


if __name__ == "__main__":
    variant = sys.argv[1] if len(sys.argv) > 1 else "A"
    out_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "entry.png")
    img = build(variant)
    compose_path = os.path.join(HERE, "compose_%s.png" % variant)
    img.save(compose_path)
    finalize(img, out_path)
    print("variant", variant, "->", out_path)
