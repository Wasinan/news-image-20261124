#!/usr/bin/env python3
"""Build one 1024x1024 newspaper front page summing up 24 Nov 2026.

Renders the four verified stories of the day with PIL only: a masthead,
a full-width lead panel and three columns below it. Run it and it writes
news-image-20261124.png next to this script.
"""

import hashlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT_NAME = "news-image-20261124.png"

CANVAS = 1024
MARGIN = 36
PAPER = (245, 239, 224)
PANEL = (255, 253, 245)
INK = (26, 26, 26)
SOFT = (74, 74, 66)
RULE = (26, 26, 26)
RED = (178, 28, 28)
BLUE = (30, 58, 95)
GOLD = (176, 132, 30)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def pick(size, bold=False, serif=False):
    name = "DejaVuSerif-Bold.ttf" if serif else (
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    )
    return ImageFont.truetype(str(FONT_DIR / name), size)


def wrap(draw, text, font, width):
    """Greedy word wrap measured with the real font."""
    lines = []
    for chunk in text.split("\n"):
        words = chunk.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=font) <= width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def block(draw, xy, text, font, width, fill=INK, gap=6):
    """Draw wrapped text, return the y just below the last line."""
    x, y = xy
    for line in wrap(draw, text, font, width):
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + gap
    return y


def fit_block(draw, xy, text, size, width, max_bottom, fill=SOFT, gap=4):
    """Draw body text shrunk until it fits above max_bottom.

    Drops the font size step by step; as a last resort trims the text
    with an ellipsis so nothing ever spills past the panel edge.
    """
    x, y = xy
    size = size
    while size >= 13:
        font = pick(size)
        lines = wrap(draw, text, font, width)
        if y + len(lines) * (size + gap) <= max_bottom:
            for line in lines:
                draw.text((x, y), line, font=font, fill=fill)
                y += size + gap
            return y
        size -= 1
    font = pick(13)
    lines = wrap(draw, text, font, width)
    room = max(1, (max_bottom - y) // (13 + gap))
    for line in lines[:room]:
        draw.text((x, y), line, font=font, fill=fill)
        y += 13 + gap
    if len(lines) > room and room > 0:
        draw.text((x, y - 13 - gap), lines[room - 1].rstrip(". ") + "…", font=font, fill=fill)
    return y


def headline_fit(draw, text, font_size, width, bold=True):
    """Largest bold font (<= font_size) that wraps the headline in 3 lines."""
    size = font_size
    while size > 18:
        font = pick(size, bold=bold)
        if len(wrap(draw, text, font, width)) <= 3:
            return font
        size -= 2
    return pick(18, bold=bold)


def radar(draw, cx, cy, radius):
    for step in range(3, 0, -1):
        ring = radius * step / 3
        draw.ellipse(
            [cx - ring, cy - ring, cx + ring, cy + ring],
            outline=BLUE,
            width=2,
        )
    draw.line([cx - radius, cy, cx + radius, cy], fill=BLUE, width=1)
    draw.line([cx, cy - radius, cx, cy + radius], fill=BLUE, width=1)
    draw.line([cx, cy, cx + radius * 0.7, cy - radius * 0.7], fill=RED, width=3)
    draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED)
    draw.ellipse(
        [cx + radius * 0.45 - 4, cy - radius * 0.45 - 4,
         cx + radius * 0.45 + 4, cy - radius * 0.45 + 4],
        fill=RED,
    )


def bars(draw, x, y, width, height):
    tops = [0.45, 0.7, 1.0]
    bw = width // 4
    for i, top in enumerate(tops):
        bx = x + i * (bw + 8)
        bh = int(height * top)
        draw.rectangle([bx, y + height - bh, bx + bw, y + height], fill=BLUE)
    draw.line([x, y + height, x + width, y + height], fill=INK, width=2)


def jet(draw, cx, cy, scale):
    s = scale
    fuselage = [
        (cx - 58 * s, cy + 4 * s),
        (cx + 56 * s, cy - 10 * s),
        (cx + 58 * s, cy - 2 * s),
        (cx - 52 * s, cy + 14 * s),
    ]
    draw.polygon(fuselage, fill=INK)
    wing = [
        (cx - 8 * s, cy + 2 * s),
        (cx - 26 * s, cy + 32 * s),
        (cx - 38 * s, cy + 4 * s),
    ]
    draw.polygon(wing, fill=INK)
    tail = [
        (cx - 44 * s, cy + 0 * s),
        (cx - 56 * s, cy - 16 * s),
        (cx - 62 * s, cy + 2 * s),
    ]
    draw.polygon(tail, fill=INK)
    draw.line(
        [cx - 78 * s, cy + 22 * s, cx - 60 * s, cy + 18 * s],
        fill=RED,
        width=3,
    )


def chip(draw, cx, cy, side):
    half = side // 2
    draw.rounded_rectangle(
        [cx - half, cy - half, cx + half, cy + half],
        radius=10,
        fill=INK,
    )
    inner = side // 2 - 14
    draw.rounded_rectangle(
        [cx - inner, cy - inner, cx + inner, cy + inner],
        radius=6,
        outline=GOLD,
        width=3,
    )
    for i in range(4):
        off = -side // 2 + 16 + i * (side - 32) // 3
        draw.line([cx + off, cy - half - 12, cx + off, cy - half], fill=INK, width=4)
        draw.line([cx + off, cy + half, cx + off, cy + half + 12], fill=INK, width=4)
        draw.line([cx - half - 12, cy + off, cx - half, cy + off], fill=INK, width=4)
        draw.line([cx + half, cy + off, cx + half + 12, cy + off], fill=INK, width=4)


LEAD = {
    "kicker": "LEAD  ·  NATO AIRSPACE",
    "title": "Russian drone strays into Poland as NATO jets watch",
    "body": (
        "A Russian drone briefly crossed into Polish airspace near Dorohusk "
        "overnight, during a barrage on western Ukraine. Warsaw activated "
        "air defences and authorised a shoot-down, then held fire as the "
        "drone turned east — the risk to civilians below was too high. It is "
        "the second breach in four days; NATO is sending an AWACS to "
        "bolster Polish skies. It follows Friday's landing of three "
        "Russian cruise missiles in Poland."
    ),
}

COLUMNS = [
    {
        "kicker": "THE HUMAN COST",
        "title": "700,000 Russian war dead, leaked records reveal",
        "body": (
            "A Meduza–Mediazona probe of leaked Rosstat death records counts "
            "at least 490,000 registered Russian military deaths since "
            "February 2022. Adjusted for the missing and late registrations, "
            "the toll passes 700,000 — Moscow's deadliest war since 1945, "
            "one in every 200 Russians."
        ),
        "art": "bars",
    },
    {
        "kicker": "SAME DAY, OTHER SKIES",
        "title": "Russian jets trigger air-raid alert off South Korea",
        "body": (
            "Hours later, Russian military aircraft entered South Korea's "
            "air-defence zone near Ulleungdo island. Jets scrambled, sirens "
            "sounded and 8,700 islanders were told to shelter. Seoul says "
            "its airspace was not breached, and it will summon Moscow's "
            "defence attaché in protest."
        ),
        "art": "jet",
    },
    {
        "kicker": "MARKETS  ·  TECH",
        "title": "Nvidia board in U-turn: Huang is CEO again",
        "body": (
            "Nvidia's board unanimously reinstated Jensen Huang as chief "
            "executive, reversing course days after ruling out his return. "
            "Shares whipsawed — and filings show Donald Trump made up to "
            "$15 million on Nvidia stock around the comeback. The reversal "
            "caps a chaotic week for the chipmaker."
        ),
        "art": "chip",
    },
]


def paint():
    img = Image.new("RGB", (CANVAS, CANVAS), PAPER)
    draw = ImageDraw.Draw(img)

    # Double outer frame.
    draw.rectangle([10, 10, CANVAS - 11, CANVAS - 11], outline=RULE, width=3)
    draw.rectangle([20, 20, CANVAS - 21, CANVAS - 21], outline=RULE, width=1)

    # Masthead.
    title_font = pick(58, serif=True)
    title = "THE WORLD IN ONE PAGE"
    tw = draw.textlength(title, font=title_font)
    draw.text(((CANVAS - tw) / 2, 34), title, font=title_font, fill=INK)
    draw.line([MARGIN, 118, CANVAS - MARGIN, 118], fill=RULE, width=3)
    date_font = pick(20, bold=True)
    dateline = "TUESDAY, 24 NOVEMBER 2026  ·  FOUR STORIES THAT MATTER"
    dw = draw.textlength(dateline, font=date_font)
    draw.text(((CANVAS - dw) / 2, 130), dateline, font=date_font, fill=RED)
    draw.line([MARGIN, 164, CANVAS - MARGIN, 164], fill=RULE, width=1)

    # Lead panel.
    lead_top, lead_bottom = 180, 528
    draw.rectangle(
        [MARGIN, lead_top, CANVAS - MARGIN, lead_bottom], fill=PANEL, outline=RULE, width=2
    )
    kick_font = pick(20, bold=True)
    draw.text((MARGIN + 22, lead_top + 16), LEAD["kicker"], font=kick_font, fill=RED)
    head_font = headline_fit(draw, LEAD["title"], 46, 680)
    y = block(
        draw,
        (MARGIN + 22, lead_top + 48),
        LEAD["title"],
        head_font,
        680,
        gap=2,
    )
    fit_block(draw, (MARGIN + 22, y + 10), LEAD["body"], 20, 680, lead_bottom - 16, gap=5)
    radar(draw, 852, 340, 74)
    cap_font = pick(15)
    caption = "POLISH SKIES, 23–24 NOV"
    cw = draw.textlength(caption, font=cap_font)
    draw.text((852 - cw / 2, 440), caption, font=cap_font, fill=SOFT)

    # Divider between lead and columns.
    draw.line([MARGIN, 548, CANVAS - MARGIN, 548], fill=RULE, width=2)

    # Three columns.
    col_w = 300
    gap_x = 26
    col_top = 566
    col_bottom = 946
    art_fns = {"bars": bars, "jet": jet, "chip": chip}
    for i, col in enumerate(COLUMNS):
        x0 = MARGIN + i * (col_w + gap_x)
        draw.rectangle([x0, col_top, x0 + col_w, col_bottom], fill=PANEL, outline=RULE, width=2)
        inner = x0 + 18
        width = col_w - 36
        if col["art"] == "bars":
            bars(draw, inner + 30, col_top + 18, width - 60, 56)
        elif col["art"] == "jet":
            jet(draw, x0 + col_w // 2, col_top + 48, 0.9)
        else:
            chip(draw, x0 + col_w // 2, col_top + 48, 62)
        cy = col_top + 96
        draw.text((inner, cy), col["kicker"], font=pick(16, bold=True), fill=RED)
        cy += 28
        hfont = headline_fit(draw, col["title"], 27, width)
        cy = block(draw, (inner, cy), col["title"], hfont, width, gap=2)
        fit_block(draw, (inner, cy + 10), col["body"], 18, width, col_bottom - 14, gap=4)

    # Footer.
    foot_font = pick(15)
    foot = "Sources: Reuters · Meduza / Mediazona · Yonhap · AP  —  24 Nov 2026"
    fw = draw.textlength(foot, font=foot_font)
    draw.text(((CANVAS - fw) / 2, 964), foot, font=foot_font, fill=SOFT)

    out = HERE / OUT_NAME
    img.save(out, "PNG")
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    print(f"wrote {out} ({img.size[0]}x{img.size[1]})")
    print(f"sha256 {digest}")
    return out


if __name__ == "__main__":
    paint()
