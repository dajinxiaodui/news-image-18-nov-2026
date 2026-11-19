#!/usr/bin/env python3
"""News image: one picture of Wednesday 18 November 2026.

A pure-stdlib program (zlib + struct + math only). It draws a newspaper
front page straight into pixels: a 5x7 bitmap font carried in this file,
flat-colour pictograms, and the day's six biggest stories, each checked
against the day's reporting (Reuters, AP, Al Jazeera, Anadolu, GMA, Fed).
No network, no clock, no randomness: two runs write byte-identical PNGs.

Layout (1024 x 1024): masthead with the date, a lead panel on the markets
and the Fed minutes, six story panels in a 3 x 2 grid, an "also today"
ticker and a sources line.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (246, 241, 227)
INK = (22, 35, 58)
RED = (179, 38, 30)
TEAL = (14, 110, 106)
NAVY = (29, 78, 137)
AMBER = (217, 142, 4)
GREEN = (46, 125, 50)
PURPLE = (91, 75, 138)
GREY = (112, 116, 120)
WHITE = (255, 255, 255)
CREAM = (232, 222, 196)
LIGHTRED = (244, 214, 210)
LIGHTTEAL = (205, 232, 228)
LIGHTNAVY = (210, 224, 240)
LIGHTAMBER = (248, 232, 196)
LIGHTGREEN = (214, 236, 214)
LIGHTPURPLE = (226, 220, 240)
DARKGREEN = (27, 94, 32)

# ------------------------------------------------------------------ font
# 5x7 bitmap font: 7 rows of 5 bits per glyph, '#' on, '.' off.
# Uppercase, digits and the punctuation this page needs.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
}

# ------------------------------------------------------------------ canvas
class Canvas:
    """A flat RGB pixel buffer with tiny drawing helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        r, g, b = c
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = r, g, b

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0, y0, t, t, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            d = r * r - (yy - cy) ** 2
            dx = int(d ** 0.5) if d >= 0 else 0
            self.fill_rect(cx - dx, yy, dx * 2 + 1, 1, c)

    def ring(self, cx, cy, r, c, t=3):
        for k in range(t):
            rr = r - k
            for a in range(0, 360, 2):
                x = cx + int(rr * math.cos(math.radians(a)))
                y = cy + int(rr * math.sin(math.radians(a)))
                self.set(x, y, c)

    def tri(self, pts, c):
        (x0, y0), (x1, y1), (x2, y2) = pts
        for y in range(min(y0, y1, y2), max(y0, y1, y2) + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay != by and min(ay, by) <= y < max(ay, by):
                    xs.append(ax + (y - ay) * (bx - ax) // (by - ay))
            if len(xs) >= 2:
                self.fill_rect(min(xs), y, max(xs) - min(xs) + 1, 1, c)

    # -- text ------------------------------------------------------
    def text(self, x, y, s, scale, c, align="left"):
        s = s.upper()
        adv = 6 * scale
        width = len(s) * adv - scale
        if align == "center":
            x -= width // 2
        elif align == "right":
            x -= width
        for k, ch in enumerate(s):
            glyph = FONT.get(ch, FONT[' '])
            ox = x + k * adv
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.fill_rect(ox + col * scale, y + row * scale,
                                       scale, scale, c)
        return width

    def wrap(self, s, max_chars):
        words = s.upper().split()
        lines, cur = [], ""
        for word in words:
            if cur and len(cur) + 1 + len(word) > max_chars:
                lines.append(cur)
                cur = word
            else:
                cur = f"{cur} {word}".strip()
        if cur:
            lines.append(cur)
        return lines


def chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    idat = zlib.compress(bytes(raw), 6)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")

# ------------------------------------------------------------------ pictograms
def pic_summit(cv, x, y, w, h):
    """Three flags on poles: the Shenzhen three-way summit."""
    cv.fill_rect(x, y, w, h, NAVY)
    cv.fill_rect(x, y + h - 16, w, 16, (18, 52, 96))
    cols = (RED, WHITE, AMBER)
    for k, col in enumerate(cols):
        px = x + 66 + k * 84
        cv.vline(px, y + 12, 52, WHITE, 3)
        cv.tri([(px + 3, y + 12), (px + 52, y + 24), (px + 3, y + 36)], col)
    cv.line(x + 40, y + h - 26, x + w - 40, y + h - 26, WHITE, 3)


def pic_drone(cv, x, y, w, h):
    """A drone over a desert base at night."""
    cv.fill_rect(x, y, w, h, INK)
    for k in range(30):
        cv.set(x + 12 + (k * 97) % (w - 24), y + 8 + (k * 53) % 26, (140, 160, 200))
    cv.fill_rect(x, y + h - 22, w, 22, (60, 52, 40))
    for bx in (x + 30, x + w - 90):
        cv.fill_rect(bx, y + h - 44, 60, 22, (120, 110, 90))
    cx, cy = x + w // 2, y + 34
    cv.fill_rect(cx - 34, cy - 8, 68, 16, (200, 210, 220))
    cv.fill_rect(cx - 10, cy - 4, 20, 26, (160, 170, 185))
    for dx, dy in ((-44, -14), (44, -14), (-44, 14), (44, 14)):
        cv.line(cx + dx // 2, cy, cx + dx, cy + dy, (160, 170, 185), 2)
        cv.hline(cx + dx - 12, cy + dy, 24, (220, 225, 235), 2)
    cv.circle(cx, cy + 30, 4, RED)
    cv.line(cx - 4, cy + 30, cx + 4, cy + 30, RED, 2)


def pic_ballot(cv, x, y, w, h):
    """A ballot box with a checked ballot: the Alaska Senate call."""
    cv.fill_rect(x, y, w, h, LIGHTNAVY)
    cx = x + w // 2
    cv.fill_rect(cx - 44, y + 6, 88, 26, WHITE)
    cv.line(cx - 40, y + 20, cx - 32, y + 28, RED, 3)
    cv.line(cx - 32, y + 28, cx - 16, y + 10, RED, 3)
    cv.fill_rect(cx - 62, y + 36, 124, 40, WHITE)
    cv.fill_rect(cx - 62, y + 36, 124, 4, INK)
    cv.fill_rect(cx - 8, y + 36, 16, 4, INK)
    cv.text(cx, y + 48, "56 - 44", 2, NAVY, "center")
    cv.fill_rect(x + 30, y + h - 12, w - 60, 3, INK)


def pic_chip(cv, x, y, w, h):
    """A processor chip with pins: Nvidia's quarter."""
    cv.fill_rect(x, y, w, h, INK)
    cx, cy = x + w // 2, y + h // 2
    for k in range(6):
        px = cx - 50 + k * 20
        cv.vline(px, y + 6, 14, AMBER, 3)
        cv.vline(px, y + h - 20, 14, AMBER, 3)
        py = cy - 34 + k * 14
        cv.hline(x + 6, py, 14, AMBER, 3)
        cv.hline(x + w - 20, py, 14, AMBER, 3)
    cv.fill_rect(cx - 42, cy - 30, 84, 60, GREEN)
    cv.fill_rect(cx - 30, cy - 18, 60, 36, DARKGREEN)
    cv.text(cx, cy - 9, "NVDA", 2, WHITE, "center")


def pic_tank(cv, x, y, w, h):
    """A tank on a road: the Gaza ground operation."""
    cv.fill_rect(x, y, w, h, CREAM)
    cv.fill_rect(x, y + h - 20, w, 20, (120, 100, 70))
    cv.hline(x, y + h - 20, w, INK, 2)
    cx, cy = x + w // 2, y + h // 2 - 6
    cv.fill_rect(cx - 70, cy - 6, 140, 22, (90, 100, 80))
    cv.fill_rect(cx - 44, cy - 26, 70, 22, (70, 80, 62))
    cv.line(cx + 26, cy - 18, cx + 84, cy - 26, (70, 80, 62), 6)
    for k in range(6):
        wx = cx - 58 + k * 24
        cv.circle(wx, cy + 20, 8, INK)
        cv.circle(wx, cy + 20, 3, GREY)


def pic_quad(cv, x, y, w, h):
    """Four flags in a row: the Quad leaders in Manila."""
    cv.fill_rect(x, y, w, h, LIGHTTEAL)
    cols = (RED, NAVY, AMBER, GREEN)
    for k, col in enumerate(cols):
        px = x + 46 + k * 64
        cv.vline(px, y + 12, 56, INK, 3)
        cv.tri([(px + 3, y + 12), (px + 40, y + 22), (px + 3, y + 32)], col)
    cv.hline(x + 24, y + h - 16, w - 48, INK, 3)


PICS = {"summit": pic_summit, "drone": pic_drone, "ballot": pic_ballot,
        "chip": pic_chip, "tank": pic_tank, "quad": pic_quad}

# ------------------------------------------------------------------ stories
# Each story: kicker, headline lines (pre-wrapped, <= 12 chars a line at
# scale 4), summary (wrapped by the renderer), pictogram, panel tint.
STORIES = [
    {"kicker": "DIPLOMACY - SHENZHEN", "pic": "summit", "tint": LIGHTNAVY,
     "head": ["XI, PUTIN", "MEET IN", "SHENZHEN"],
     "sum": "TRUMP ARRIVES FOR FIRST THREE-WAY SUMMIT ON 19 NOV"},
    {"kicker": "GULF - WAR", "pic": "drone", "tint": LIGHTPURPLE,
     "head": ["IRAN DRONES", "HIT US BASE", "IN KUWAIT"],
     "sum": "KUWAIT AND BAHRAIN SAY THEY INTERCEPTED THE ATTACKS"},
    {"kicker": "US POLITICS", "pic": "ballot", "tint": LIGHTTEAL,
     "head": ["PELTOLA WINS", "ALASKA; DEMS", "TAKE 56-44"],
     "sum": "FIRST ALASKA NATIVE IN SENATE; NINTH MIDTERM FLIP"},
    {"kicker": "TECH - CHIPS", "pic": "chip", "tint": LIGHTAMBER,
     "head": ["NVIDIA SALES", "$115.8BN,", "UP 103%"],
     "sum": "BEATS FORECASTS; BOARD RULES OUT HUANG RETURN"},
    {"kicker": "GAZA", "pic": "tank", "tint": LIGHTRED,
     "head": ["ISRAEL MOVES", "INTO CENTRAL", "GAZA"],
     "sum": "FIRST GROUND MOVE SINCE 2025 TRUCE; TANKS WEST OF YELLOW LINE"},
    {"kicker": "ASIA - QUAD", "pic": "quad", "tint": LIGHTGREEN,
     "head": ["QUAD MEETS", "IN MANILA;", "TRADE DEAL"],
     "sum": "TRUMP HAILS BIG US-PHILIPPINES PACT; FIRST MEET IN 2 YEARS"},
]

TICKER = [
    "FED MINUTES: ALMOST ALL SEE MORE HIKES; WALLER EYES 50BP IN DEC",
    "CYCLONE AKVAN NEARS INDIA; ODISHA MOVES PEOPLE TO SHELTERS",
    "UK SANCTIONS 8 FIRMS OVER WEST BANK SETTLEMENTS",
    "INDIA-US TRADE TALKS NEARLY DONE; SIGNING DELAYED",
]

# ------------------------------------------------------------------ page
def lead_panel(cv, lx, ly, lw, lh):
    cv.fill_rect(lx, ly, lw, lh, LIGHTRED)
    for t in range(2):
        cv.hline(lx, ly + t, lw, INK, 1)
        cv.hline(lx, ly + lh - 1 - t, lw, INK, 1)
        cv.vline(lx + t, ly, lh, INK, 1)
        cv.vline(lx + lw - 1 - t, ly, lh, INK, 1)
    # mixed market bars: Dow and S&P down, Nasdaq up, gold down hard
    bx0, base = lx + 26, ly + 118
    cv.hline(bx0 - 8, base, 272, INK, 3)
    bars = [("DOW", -1.11, RED), ("S&P", -0.23, RED),
            ("NAS", 0.42, GREEN), ("GOLD", -3.16, RED)]
    for k, (name, pct, col) in enumerate(bars):
        x = bx0 + k * 68
        hgt = max(4, int(abs(pct) * 26))
        if pct < 0:
            cv.fill_rect(x, base - hgt, 44, hgt, col)
        else:
            cv.fill_rect(x, base, 44, hgt, col)
        cv.text(x + 22, base + 10, name, 2, INK, "center")
        cv.text(x + 22, base + 26, f"{pct:+.1f}%", 2, col, "center")
    tx = lx + 300
    cv.text(tx, ly + 16, "NEW YORK - MARKETS", 2, RED)
    cv.text(tx, ly + 42, "DOW SINKS, GOLD", 5, INK)
    cv.text(tx, ly + 84, "CRASHES BELOW $3,800", 5, RED)
    cv.text(tx, ly + 130, "DOW -561 TO 50,198; S&P -0.2% TO 7,324", 2, INK)
    cv.text(tx, ly + 150, "NASDAQ +0.4% TO 24,430; GOLD -$122 TO $3,742", 2, INK)


def render():
    cv = Canvas(W, H, PAPER)
    # masthead
    cv.text(W // 2, 26, "THE WORLD IN ONE DAY", 3, GREY, "center")
    cv.text(W // 2, 56, "WEDNESDAY, 18 NOVEMBER 2026", 6, INK, "center")
    cv.hline(28, 116, W - 56, INK, 4)
    cv.hline(28, 124, W - 56, INK, 1)

    # lead: markets and the Fed
    lead_panel(cv, 28, 134, W - 56, 176)

    # grid of six stories
    gx, gy = 28, 322
    cw, ch, gap = 312, 268, 15
    for n, st in enumerate(STORIES):
        px = gx + (n % 3) * (cw + gap)
        py = gy + (n // 3) * (ch + 8)
        cv.fill_rect(px, py, cw, ch, st["tint"])
        for t in range(2):
            cv.hline(px, py + t, cw, INK, 1)
            cv.hline(px, py + ch - 1 - t, cw, INK, 1)
            cv.vline(px + t, py, ch, INK, 1)
            cv.vline(px + cw - 1 - t, py, ch, INK, 1)
        PICS[st["pic"]](cv, px + 2, py + 2, cw - 4, 88)
        cv.text(px + 14, py + 98, st["kicker"], 2, RED)
        yy = py + 120
        for line in st["head"]:
            cv.text(px + 14, yy, line, 4, INK)
            yy += 32
        for line in cv.wrap(st["sum"], 24):
            cv.text(px + 14, yy, line, 2, INK)
            yy += 15

    # ticker
    ty = 878
    cv.fill_rect(28, ty, W - 56, 112, INK)
    cv.text(48, ty + 12, "ALSO TODAY", 3, AMBER)
    for k, item in enumerate(TICKER):
        ix = 48 + (k % 2) * 484
        iy = ty + 44 + (k // 2) * 34
        cv.fill_rect(ix, iy + 3, 10, 10, AMBER)
        for j, line in enumerate(cv.wrap(item, 38)[:2]):
            cv.text(ix + 18, iy + j * 15, line, 2, WHITE)

    # footer
    cv.hline(28, 1000, W - 56, INK, 1)
    cv.text(W // 2, 1008, "REPORTED ON 18 NOVEMBER 2026 - REUTERS, AP, AL JAZEERA, ANADOLU, GMA",
            2, GREY, "center")
    return cv


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    png = encode_png(render())
    with open(os.path.join(out, "entry.png"), "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
