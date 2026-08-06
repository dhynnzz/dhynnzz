import os
import random
import requests
from datetime import datetime

USERNAME = "dhynnzz"

WIDTH = 1200
HEIGHT = 390

BG = "#0d1117"
CARD = "#0d1117"
BORDER = "#30363d"
GRID_EMPTY = "#161b22"

GREEN_1 = "#0e4429"
GREEN_2 = "#006d32"
GREEN_3 = "#26a641"
GREEN_4 = "#39d353"

CYAN = "#00d9ff"
PURPLE = "#a855f7"
TEXT = "#f0f6fc"
MUTED = "#8b949e"

token = os.environ.get("GITHUB_TOKEN", "")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}

query = """
query($userName: String!) {
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

data = response.json()

if "errors" in data:
    raise RuntimeError(data["errors"])

calendar = (
    data["data"]["user"]["contributionsCollection"]
    ["contributionCalendar"]
)

weeks = calendar["weeks"]
total_contributions = calendar["totalContributions"]

# =========================================================
# CALCULATE STATS
# =========================================================

active_days = 0
max_day = 0

for week in weeks:
    for day in week["contributionDays"]:
        count = day["contributionCount"]

        if count > 0:
            active_days += 1

        max_day = max(max_day, count)

# XP dibuat berdasarkan aktivitas nyata
xp = min(
    100,
    int((active_days / 365) * 100)
)

# Level berdasarkan total contributions
level = max(
    1,
    (total_contributions // 100) + 1
)

# =========================================================
# SVG START
# =========================================================

svg = []

svg.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{WIDTH}" height="{HEIGHT}" '
    f'viewBox="0 0 {WIDTH} {HEIGHT}">'
)

# Background
svg.append(
    f'<rect width="{WIDTH}" height="{HEIGHT}" '
    f'rx="20" fill="{BG}"/>'
)

# Border
svg.append(
    f'<rect x="1" y="1" '
    f'width="{WIDTH - 2}" height="{HEIGHT - 2}" '
    f'rx="19" fill="none" '
    f'stroke="{BORDER}" stroke-width="2"/>'
)

# =========================================================
# HEADER
# =========================================================

svg.append(
    f'<text x="45" y="48" '
    f'fill="{TEXT}" '
    f'font-family="Arial, sans-serif" '
    f'font-size="23" '
    f'font-weight="bold">'
    f'DEVELOPER QUEST'
    f'</text>'
)

svg.append(
    f'<text x="45" y="73" '
    f'fill="{MUTED}" '
    f'font-family="Arial, sans-serif" '
    f'font-size="13">'
    f'Building my journey, one commit at a time.'
    f'</text>'
)

# Online indicator
svg.append(
    f'<circle cx="1040" cy="43" r="5" fill="{GREEN_4}">'
    f'<animate attributeName="opacity" '
    f'values="1;0.3;1" dur="2s" '
    f'repeatCount="indefinite"/>'
    f'</circle>'
)

svg.append(
    f'<text x="1055" y="48" '
    f'fill="{GREEN_4}" '
    f'font-family="monospace" '
    f'font-size="12" '
    f'font-weight="bold">'
    f'ONLINE'
    f'</text>'
)

# Level
svg.append(
    f'<text x="1150" y="48" '
    f'text-anchor="end" '
    f'fill="{PURPLE}" '
    f'font-family="monospace" '
    f'font-size="12">'
    f'LVL {level:02d}'
    f'</text>'
)

# Divider
svg.append(
    f'<line x1="45" y1="90" '
    f'x2="1155" y2="90" '
    f'stroke="{BORDER}"/>'
)

# =========================================================
# CONTRIBUTION GRID
# =========================================================

START_X = 45
START_Y = 115

CELL = 13
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

        level_name = day["contributionLevel"]

        color = level_map.get(
            level_name,
            GRID_EMPTY
        )

        count = day["contributionCount"]

        if count > 0:
            active_cells.append(
                (px, py, count)
            )

        svg.append(
            f'<rect '
            f'x="{px}" y="{py}" '
            f'width="{CELL}" height="{CELL}" '
            f'rx="3" '
            f'fill="{color}"/>'
        )

# =========================================================
# QUEST CHECKPOINTS
# =========================================================

if active_cells:

    checkpoint_indexes = [
        len(active_cells) // 4,
        len(active_cells) // 2,
        (len(active_cells) * 3) // 4,
    ]

    for index in checkpoint_indexes:

        if index < len(active_cells):

            cx, cy, _ = active_cells[index]

            svg.append(
                f'<circle '
                f'cx="{cx + CELL / 2}" '
                f'cy="{cy + CELL / 2}" '
                f'r="10" '
                f'fill="none" '
                f'stroke="{CYAN}" '
                f'stroke-width="1" '
                f'opacity="0.4">'
                f'<animate '
                f'attributeName="r" '
                f'values="7;13;7" '
                f'dur="3s" '
                f'repeatCount="indefinite"/>'
                f'</circle>'
            )

# =========================================================
# DEVELOPER CHARACTER
# =========================================================

if active_cells:
    hero_x, hero_y, _ = active_cells[-1]
else:
    hero_x = 900
    hero_y = 150

hero_center_x = hero_x + CELL / 2
hero_center_y = hero_y + CELL / 2

# Glow
svg.append(
    f'<circle '
    f'cx="{hero_center_x}" '
    f'cy="{hero_center_y}" '
    f'r="18" '
    f'fill="{CYAN}" '
    f'opacity="0.10">'
    f'<animate '
    f'attributeName="r" '
    f'values="14;23;14" '
    f'dur="2s" '
    f'repeatCount="indefinite"/>'
    f'</circle>'
)

# Head
svg.append(
    f'<circle '
    f'cx="{hero_center_x}" '
    f'cy="{hero_center_y - 2}" '
    f'r="7" '
    f'fill="{CYAN}"/>'
)

# Eyes
svg.append(
    f'<circle '
    f'cx="{hero_center_x - 2.5}" '
    f'cy="{hero_center_y - 3}" '
    f'r="1.2" '
    f'fill="#ffffff"/>'
)

svg.append(
    f'<circle '
    f'cx="{hero_center_x + 2.5}" '
    f'cy="{hero_center_y - 3}" '
    f'r="1.2" '
    f'fill="#ffffff"/>'
)

# Developer label
svg.append(
    f'<text '
    f'x="{hero_center_x}" '
    f'y="{hero_center_y + 23}" '
    f'text-anchor="middle" '
    f'fill="{CYAN}" '
    f'font-family="monospace" '
    f'font-size="8">'
    f'DEV'
    f'</text>'
)

# =========================================================
# PARTICLES
# =========================================================

random.seed(42)

symbols = [
    "&lt;/&gt;",
    "{ }",
    "01",
    "git",
    "+",
]

for _ in range(10):

    x = random.randint(100, 1080)
    y = random.randint(105, 215)

    symbol = random.choice(symbols)

    color = random.choice([
        CYAN,
        PURPLE,
        GREEN_4,
    ])

    duration = random.randint(3, 6)

    svg.append(
        f'<text '
        f'x="{x}" y="{y}" '
        f'fill="{color}" '
        f'opacity="0.25" '
        f'font-family="monospace" '
        f'font-size="9">'
        f'{symbol}'
        f'<animate '
        f'attributeName="opacity" '
        f'values="0.15;0.65;0.15" '
        f'dur="{duration}s" '
        f'repeatCount="indefinite"/>'
        f'</text>'
    )

# =========================================================
# XP SECTION
# =========================================================

svg.append(
    f'<text '
    f'x="45" y="265" '
    f'fill="{TEXT}" '
    f'font-family="monospace" '
    f'font-size="12" '
    f'font-weight="bold">'
    f'XP'
    f'</text>'
)

BAR_X = 80
BAR_Y = 255
BAR_WIDTH = 920
BAR_HEIGHT = 12

svg.append(
    f'<rect '
    f'x="{BAR_X}" y="{BAR_Y}" '
    f'width="{BAR_WIDTH}" '
    f'height="{BAR_HEIGHT}" '
    f'rx="6" '
    f'fill="{GRID_EMPTY}"/>'
)

progress_width = int(
    BAR_WIDTH * (xp / 100)
)

svg.append(
    f'<rect '
    f'x="{BAR_X}" y="{BAR_Y}" '
    f'width="{progress_width}" '
    f'height="{BAR_HEIGHT}" '
    f'rx="6" '
    f'fill="{CYAN}">'
    f'<animate '
    f'attributeName="opacity" '
    f'values="0.75;1;0.75" '
    f'dur="2s" '
    f'repeatCount="indefinite"/>'
    f'</rect>'
)

svg.append(
    f'<text '
    f'x="1020" y="265" '
    f'fill="{CYAN}" '
    f'font-family="monospace" '
    f'font-size="12" '
    f'font-weight="bold">'
    f'{xp}%'
    f'</text>'
)

# =========================================================
# STATS
# =========================================================

svg.append(
    f'<text x="45" y="305" '
    f'fill="{GREEN_4}" '
    f'font-family="monospace" '
    f'font-size="12">'
    f'● {total_contributions} CONTRIBUTIONS'
    f'</text>'
)

svg.append(
    f'<text x="310" y="305" '
    f'fill="{CYAN}" '
    f'font-family="monospace" '
    f'font-size="12">'
    f'● {active_days} ACTIVE DAYS'
    f'</text>'
)

svg.append(
    f'<text x="550" y="305" '
    f'fill="{PURPLE}" '
    f'font-family="monospace" '
    f'font-size="12">'
    f'● BEST DAY {max_day} COMMITS'
    f'</text>'
)

# =========================================================
# JOURNEY STATUS
# =========================================================

svg.append(
    f'<text x="45" y="340" '
    f'fill="{MUTED}" '
    f'font-family="monospace" '
    f'font-size="11">'
    f'◉ LEARNING'
    f'</text>'
)

svg.append(
    f'<text x="190" y="340" '
    f'fill="{MUTED}" '
    f'font-family="monospace" '
    f'font-size="11">'
    f'◉ BUILDING'
    f'</text>'
)

svg.append(
    f'<text x="335" y="340" '
    f'fill="{MUTED}" '
    f'font-family="monospace" '
    f'font-size="11">'
    f'◉ IMPROVING'
    f'</text>'
)

# =========================================================
# FOOTER
# =========================================================

now = datetime.now().strftime(
    "%d %b %Y"
)

svg.append(
    f'<text '
    f'x="45" y="370" '
    f'fill="{MUTED}" '
    f'font-family="Arial, sans-serif" '
    f'font-size="10">'
    f'Last generated: {now}'
    f'</text>'
)

svg.append(
    f'<text '
    f'x="1150" y="370" '
    f'text-anchor="end" '
    f'fill="{PURPLE}" '
    f'font-family="monospace" '
    f'font-size="11" '
    f'font-weight="bold">'
    f'@{USERNAME}'
    f'</text>'
)

svg.append("</svg>")

with open(
    "developer-journey.svg",
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "\n".join(svg)
    )

print(
    "Developer Quest generated successfully!"
)

print(
    f"Total Contributions: {total_contributions}"
)

print(
    f"Active Days: {active_days}"
)

print(
    f"XP: {xp}%"
)
