import os
import random
import requests
from datetime import datetime

USERNAME = "dhynnzz"

WIDTH = 1200
HEIGHT = 420

BG = "#0d1117"
PANEL = "#111820"
BORDER = "#30363d"
GRID_EMPTY = "#161b22"

GREEN_1 = "#0e4429"
GREEN_2 = "#006d32"
GREEN_3 = "#26a641"
GREEN_4 = "#39d353"

CYAN = "#00d9ff"
PURPLE = "#a855f7"
YELLOW = "#facc15"
RED = "#ff5c5c"

TEXT = "#e6edf3"
MUTED = "#8b949e"

TOKEN = os.environ.get("GITHUB_TOKEN", "")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

query = """
query($userName:String!) {
  user(login: $userName) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            contributionLevel
            date
          }
        }
      }
    }
  }
}
"""

response = requests.post(
    "https://api.github.com/graphql",
    json={
        "query": query,
        "variables": {"userName": USERNAME},
    },
    headers=headers,
    timeout=30,
)

response.raise_for_status()

payload = response.json()

if payload.get("errors"):
    raise RuntimeError(payload["errors"])

calendar = (
    payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
)

weeks = calendar["weeks"]
total_contributions = calendar["totalContributions"]

all_days = []

for week in weeks:
    for day in week["contributionDays"]:
        all_days.append(day)

active_days = sum(
    1 for day in all_days
    if day["contributionCount"] > 0
)

best_day = max(
    all_days,
    key=lambda day: day["contributionCount"],
)

best_day_count = best_day["contributionCount"]

# =========================
# GAME PROGRESSION
# =========================

XP_PER_LEVEL = 100

total_xp = total_contributions * 10

level = max(1, total_xp // XP_PER_LEVEL + 1)

current_level_xp = total_xp % XP_PER_LEVEL

xp_percent = current_level_xp / XP_PER_LEVEL

# =========================
# SVG HELPERS
# =========================

svg = []

def add(content):
    svg.append(content)

def text(x, y, value, size=14, color=TEXT,
         weight="normal", anchor="start",
         family="monospace"):
    add(
        f'<text x="{x}" y="{y}" '
        f'fill="{color}" '
        f'font-size="{size}" '
        f'font-weight="{weight}" '
        f'text-anchor="{anchor}" '
        f'font-family="{family}">'
        f'{value}</text>'
    )

def rect(x, y, w, h, color,
         radius=0, stroke="none",
         stroke_width=0, opacity=1):
    add(
        f'<rect x="{x}" y="{y}" '
        f'width="{w}" height="{h}" '
        f'rx="{radius}" '
        f'fill="{color}" '
        f'stroke="{stroke}" '
        f'stroke-width="{stroke_width}" '
        f'opacity="{opacity}"/>'
    )

# =========================
# SVG START
# =========================

add(
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{WIDTH}" height="{HEIGHT}" '
    f'viewBox="0 0 {WIDTH} {HEIGHT}">'
)

add("""
<style>

.title {
    font-family: monospace;
    font-weight: 800;
}

.glow {
    filter: drop-shadow(0 0 6px #00d9ff);
}

.greenGlow {
    filter: drop-shadow(0 0 5px #39d353);
}

.purpleGlow {
    filter: drop-shadow(0 0 5px #a855f7);
}

</style>
""")

# =========================
# BACKGROUND
# =========================

rect(
    1, 1,
    WIDTH - 2,
    HEIGHT - 2,
    BG,
    18,
    BORDER,
    2,
)

# =========================
# HEADER
# =========================

text(
    35, 45,
    "DEVELOPER QUEST",
    25,
    TEXT,
    "bold",
)

text(
    35, 69,
    "Building my journey, one commit at a time.",
    12,
    MUTED,
)

# Online indicator

add(
    '<circle cx="1000" cy="40" r="5" '
    'fill="#39d353" class="greenGlow">'
    '<animate attributeName="opacity" '
    'values="1;0.35;1" dur="2s" '
    'repeatCount="indefinite"/>'
    '</circle>'
)

text(
    1013, 44,
    "ONLINE",
    11,
    GREEN_4,
    "bold",
)

text(
    1135, 44,
    f"LV. {level:02}",
    11,
    PURPLE,
    "bold",
    "end",
)

# Separator

rect(
    35, 86,
    1130, 1,
    BORDER,
)

# =========================
# CONTRIBUTION MAP
# =========================

START_X = 35
START_Y = 115

CELL = 14
GAP = 4

level_map = {
    "NONE": GRID_EMPTY,
    "FIRST_QUARTILE": GREEN_1,
    "SECOND_QUARTILE": GREEN_2,
    "THIRD_QUARTILE": GREEN_3,
    "FOURTH_QUARTILE": GREEN_4,
}

active_cells = []

for x, week in enumerate(weeks):

    for y, day in enumerate(week["contributionDays"]):

        px = START_X + x * (CELL + GAP)
        py = START_Y + y * (CELL + GAP)

        color = level_map.get(
            day["contributionLevel"],
            GRID_EMPTY,
        )

        if day["contributionCount"] > 0:
            active_cells.append(
                (
                    px,
                    py,
                    day["contributionCount"],
                )
            )

        rect(
            px,
            py,
            CELL,
            CELL,
            color,
            3,
        )

# =========================
# QUEST CHECKPOINTS
# =========================

if active_cells:

    checkpoint_count = min(
        4,
        len(active_cells),
    )

    step = max(
        1,
        len(active_cells) // checkpoint_count,
    )

    checkpoints = active_cells[::step][
        :checkpoint_count
    ]

    for i, (cx, cy, count) in enumerate(checkpoints):

        add(
            f'<circle '
            f'cx="{cx + CELL / 2}" '
            f'cy="{cy + CELL / 2}" '
            f'r="10" '
            f'fill="none" '
            f'stroke="{CYAN}" '
            f'stroke-width="1" '
            f'opacity="0.65">'
            f'<animate '
            f'attributeName="r" '
            f'values="8;13;8" '
            f'dur="{2 + i * 0.4}s" '
            f'repeatCount="indefinite"/>'
            f'</circle>'
        )

# =========================
# PLAYER
# =========================

if active_cells:

    hero_x = active_cells[-1][0]
    hero_y = active_cells[-1][1]

else:

    hero_x = 600
    hero_y = 150

hero_center_x = hero_x + CELL / 2
hero_center_y = hero_y + CELL / 2

# Glow

add(
    f'<circle '
    f'cx="{hero_center_x}" '
    f'cy="{hero_center_y}" '
    f'r="20" '
    f'fill="{CYAN}" '
    f'opacity="0.12">'
    f'<animate '
    f'attributeName="r" '
    f'values="16;24;16" '
    f'dur="1.8s" '
    f'repeatCount="indefinite"/>'
    f'</circle>'
)

# Pixel character body

rect(
    hero_center_x - 7,
    hero_center_y - 7,
    14,
    14,
    CYAN,
    4,
)

# Eyes

add(
    f'<circle cx="{hero_center_x - 3}" '
    f'cy="{hero_center_y - 2}" '
    f'r="1.5" fill="white"/>'
)

add(
    f'<circle cx="{hero_center_x + 3}" '
    f'cy="{hero_center_y - 2}" '
    f'r="1.5" fill="white"/>'
)

# Legs

rect(
    hero_center_x - 6,
    hero_center_y + 7,
    4,
    4,
    CYAN,
    1,
)

rect(
    hero_center_x + 2,
    hero_center_y + 7,
    4,
    4,
    CYAN,
    1,
)

text(
    hero_center_x,
    hero_center_y + 29,
    "DEV",
    8,
    CYAN,
    "bold",
    "middle",
)

# =========================
# PARTICLES
# =========================

random.seed(42)

symbols = [
    "&lt;/&gt;",
    "{}",
    "git",
    "01",
    "+1",
]

for _ in range(12):

    px = random.randint(
        70,
        1080,
    )

    py = random.randint(
        105,
        230,
    )

    symbol = random.choice(symbols)

    color = random.choice(
        [
            CYAN,
            PURPLE,
            GREEN_4,
        ]
    )

    duration = random.randint(
        3,
        6,
    )

    add(
        f'<text x="{px}" y="{py}" '
        f'fill="{color}" '
        f'font-size="9" '
        f'font-family="monospace" '
        f'opacity="0.25">'
        f'{symbol}'
        f'<animate '
        f'attributeName="opacity" '
        f'values="0.15;0.65;0.15" '
        f'dur="{duration}s" '
        f'repeatCount="indefinite"/>'
        f'</text>'
    )

# =========================
# XP SECTION
# =========================

text(
    35,
    274,
    "XP",
    12,
    TEXT,
    "bold",
)

rect(
    75,
    264,
    870,
    10,
    GRID_EMPTY,
    5,
)

xp_width = int(
    870 * xp_percent
)

if xp_width < 15:
    xp_width = 15

add(
    f'<rect '
    f'x="75" y="264" '
    f'width="{xp_width}" '
    f'height="10" '
    f'rx="5" '
    f'fill="{CYAN}" '
    f'class="glow">'
    f'<animate '
    f'attributeName="opacity" '
    f'values="0.75;1;0.75" '
    f'dur="2s" '
    f'repeatCount="indefinite"/>'
    f'</rect>'
)

text(
    965,
    274,
    f"{current_level_xp}/{XP_PER_LEVEL} XP",
    10,
    CYAN,
    "bold",
)

# =========================
# STAT CARDS
# =========================

CARD_Y = 305
CARD_H = 65
CARD_W = 250

cards = [
    (
        35,
        "TOTAL CONTRIBUTIONS",
        str(total_contributions),
        GREEN_4,
    ),
    (
        320,
        "ACTIVE DAYS",
        str(active_days),
        CYAN,
    ),
    (
        605,
        "BEST DAY",
        f"{best_day_count} COMMITS",
        PURPLE,
    ),
    (
        890,
        "CURRENT QUEST",
        "KEEP BUILDING",
        YELLOW,
    ),
]

for x, label, value, color in cards:

    rect(
        x,
        CARD_Y,
        CARD_W,
        CARD_H,
        PANEL,
        10,
        BORDER,
        1,
    )

    add(
        f'<circle '
        f'cx="{x + 18}" '
        f'cy="{CARD_Y + 20}" '
        f'r="4" '
        f'fill="{color}"/>'
    )

    text(
        x + 30,
        CARD_Y + 24,
        label,
        9,
        MUTED,
        "bold",
    )

    text(
        x + 18,
        CARD_Y + 50,
        value,
        14,
        color,
        "bold",
    )

# =========================
# FOOTER
# =========================

today = datetime.now().strftime(
    "%d %b %Y"
)

text(
    35,
    400,
    f"Last generated: {today}",
    10,
    MUTED,
)

text(
    1160,
    400,
    f"@{USERNAME}",
    10,
    PURPLE,
    "bold",
    "end",
)

add("</svg>")

# =========================
# SAVE
# =========================

os.makedirs(
    "dist",
    exist_ok=True,
)

with open(
    "dist/developer-journey.svg",
    "w",
    encoding="utf-8",
) as file:
    file.write(
        "\n".join(svg)
    )

print(
    "Developer Quest V2 generated successfully!"
)
