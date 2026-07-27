#!/usr/bin/env python3
"""Generate assets/ascii-life.svg: an ASCII-art scene matching current hour
in Asia/Kathmandu (NPT, UTC+5:45). Run on a cron via GitHub Actions.
"""
import datetime
from zoneinfo import ZoneInfo

BG = "#0d1117"
FG = "#39d353"
DIM = "#8b949e"
ACCENT = "#58a6ff"

WIDTH, HEIGHT = 620, 240
FONT = "style=\"font-family:'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace\""


def scene_for_hour(h):
    if 5 <= h < 11:
        return "morning"
    if 11 <= h < 17:
        return "day"
    if 17 <= h < 20:
        return "evening"
    if 20 <= h < 22:
        return "night"
    return "sleep"


SCENES = {
    "morning": {
        "label": "MORNING · coffee & meditation",
        "lines": [
            "        (   )    (    )   )",
            "         )  (    )   (   (",
            "        (   )   (    )  )",
            "      _________________",
            "     |                 |",
            "     |   fresh coffee  |",
            "     |   + 10 min calm |",
            "     |_________________|",
            "          \\   ~~   /",
            "           '.____.'",
        ],
        "steam": True,
    },
    "day": {
        "label": "DAY · building stuff",
        "lines": [
            "   ┌───────────────────────────┐",
            "   │ $ go build ./...          │",
            "   │ compiling services...     │",
            "   │ [██████████████░░░░] 78%  │",
            "   │ churning the machine",
            "   └───────────────────────────┘",
        ],
        "cursor": True,
    },
    "evening": {
        "label": "EVENING · music & chill",
        "lines": [
            "      ♪   ♫      chill playlist     ♫   ♪",
            "        (  ~~~ lofi beats loop ~~~  )",
            "           o        o        o",
            "          /|\\      /|\\      /|\\",
            "          / \\      / \\      / \\",
        ],
        "notes": True,
    },
    "night": {
        "label": "NIGHT · learning",
        "lines": [
            "      ________________________",
            "     |  reading docs & papers  |",
            "     |  (o_o)  one more page..  |",
            "     |________________________|",
            "        taking notes ...",
        ],
        "blink": True,
    },
    "sleep": {
        "label": "SLEEP · lights off",
        "lines": [
            "               ________",
            "              |        |",
            "              | (-_-)  |",
            "              |________|",
            "           back at it tomorrow",
        ],
        "zzz": True,
    },
}


def build_extra(scene, base_y):
    """Small animated accents per scene, absolutely positioned."""
    parts = []
    if scene.get("steam"):
        for i, (dx, delay) in enumerate([(0, 0), (14, 0.6), (-14, 1.2)]):
            x = 250 + dx
            parts.append(f'''
  <text x="{x}" y="{base_y - 70}" fill="{DIM}" {FONT} font-size="14" opacity="0">
    ~
    <animate attributeName="opacity" values="0;0.8;0" dur="2.4s" begin="{delay}s" repeatCount="indefinite"/>
    <animateTransform attributeName="transform" type="translate" values="0,0; 0,-18" dur="2.4s" begin="{delay}s" repeatCount="indefinite"/>
  </text>''')
    if scene.get("cursor"):
        parts.append(f'''
  <rect x="470" y="{base_y - 82}" width="9" height="14" fill="{FG}">
    <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/>
  </rect>''')
    if scene.get("notes"):
        for x, delay in [(90, 0), (300, 0.4), (500, 0.8)]:
            parts.append(f'''
  <text x="{x}" y="{base_y - 95}" fill="{ACCENT}" {FONT} font-size="16">
    ♪
    <animateTransform attributeName="transform" type="translate" values="0,0; 0,-8; 0,0" dur="1.6s" begin="{delay}s" repeatCount="indefinite"/>
  </text>''')
    if scene.get("blink"):
        parts.append(f'''
  <text x="252" y="{base_y - 55}" fill="{FG}" {FONT} font-size="14">
    _
    <animate attributeName="opacity" values="1;0;1" dur="2.6s" repeatCount="indefinite"/>
  </text>''')
    if scene.get("zzz"):
        for i, (x, delay) in enumerate([(330, 0), (350, 0.9), (370, 1.8)]):
            parts.append(f'''
  <text x="{x}" y="{base_y - 60}" fill="{DIM}" {FONT} font-size="{12 + i * 2}" opacity="0">
    Z
    <animate attributeName="opacity" values="0;0.9;0" dur="3s" begin="{delay}s" repeatCount="indefinite"/>
    <animateTransform attributeName="transform" type="translate" values="0,0; 10,-24" dur="3s" begin="{delay}s" repeatCount="indefinite"/>
  </text>''')
    return "".join(parts)


def render():
    now = datetime.datetime.now(ZoneInfo("Asia/Kathmandu"))
    key = scene_for_hour(now.hour)
    scene = SCENES[key]
    time_str = now.strftime("%H:%M NPT")

    art_y0 = 88
    line_h = 16
    art_lines = "".join(
        f'<text x="30" y="{art_y0 + i * line_h}" fill="{FG}" {FONT} font-size="13" xml:space="preserve">{escape(l)}</text>\n'
        for i, l in enumerate(scene["lines"])
    )
    base_y = art_y0 + len(scene["lines"]) * line_h
    extra = build_extra(scene, base_y)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <rect width="100%" height="100%" fill="{BG}" rx="10"/>
  <text x="30" y="34" fill="{ACCENT}" {FONT} font-size="16" font-weight="bold">{scene['label']}</text>
  <text x="{WIDTH - 30}" y="34" fill="{DIM}" {FONT} font-size="13" text-anchor="end">{time_str} · Kathmandu</text>
  <line x1="30" y1="46" x2="{WIDTH - 30}" y2="46" stroke="#21262d" stroke-width="1"/>
{art_lines}{extra}
</svg>'''
    return svg


def escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


if __name__ == "__main__":
    out = render()
    with open("assets/ascii-life.svg", "w") as f:
        f.write(out)
    print("wrote assets/ascii-life.svg")
