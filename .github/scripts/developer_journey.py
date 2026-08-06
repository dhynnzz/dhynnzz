import os
import random
import requests
from datetime import datetime
from html import escape

USERNAME = "dhynnzz"

WIDTH = 1000
HEIGHT = 300

BG = "#0d1117"
GRID_EMPTY = "#161b22"

LEVEL_COLORS = [
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
]

ACCENT = "#00d9ff"
PURPLE = "#a855f7"
TEXT = "#c9d1d9"
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

weeks = (
    data["data"]["user"]["contributionsCollection"]
    ["contributionCalendar"]["weeks"]
)

svg = []

svg.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{WIDTH}" height="{HEIGHT}" '
    f'viewBox="0 0 {WIDTH} {HEIGHT}">'
)

svg.append(
    f'<rect width="{WIDTH}" height="{HEIGHT}" '
    f'rx="16" fill="{BG}"/>'
)

# Title
svg.append(
    f'<text x="40" y="42" fill="{TEXT}" '
    f'font-family="Arial, sans-serif" '
    f'font-size="20" font-weight="bold">'
    f'Developer Journey'
    f'</text>'
)

svg.append(
    f'<text x="40" y="66" fill="{MUTED}" '
    f'font-family="Arial, sans-serif" '
    f'font-size="12">'
    f'Building one commit at a time.'
    f'</text>'
)

START_X = 40
START_Y = 95
CELL = 12
GAP = 4

level_map = {
    "NONE": GRID_EMPTY,
    "FIRST_QUARTILE": LEVEL_COLORS[0],
    "SECOND_QUARTILE": LEVEL_COLORS[1],
    "THIRD_QUARTILE": LEVEL_COLORS[2],
    "FOURTH_QUARTILE": LEVEL_COLORS[3],
}

active_cells = []

# Contribution grid
for x, week in enumerate(weeks):
    for y, day in enumerate(week["contributionDays"]):

        px = START_X + x * (CELL + GAP)
        py = START_Y + y * (CELL + GAP)

        level = day["contributionLevel"]
        color = level_map.get(level, GRID_EMPTY)

        if day["contributionCount"] > 0:
            active_cells.append((px, py))

        svg.append(
            f'<rect x="{px}" y="{py}" '
            f'width="{CELL}" height="{CELL}" '
            f'rx="3" fill="{color}"/>'
        )

# Developer character position
if active_cells:
    hero_x, hero_y = active_cells[-1]
else:
    hero_x = 500
    hero_y = 150

# Glow animation
svg.append(
    f'''
<circle cx="{hero_x + 6}" cy="{hero_y + 6}"
        r="18"
        fill="{ACCENT}"
        opacity="0.15">
    <animate
        attributeName="r"
        values="15;22;15"
        dur="2s"
        repeatCount="indefinite"/>
</circle>
'''
)

# Character body
svg.append(
    f'<circle cx="{hero_x + 6}" '
    f'cy="{hero_y + 6}" '
    f'r="7" fill="{ACCENT}"/>'
)

# Eyes
svg.append(
    f'<circle cx="{hero_x + 4}" '
    f'cy="{hero_y + 4}" '
    f'r="1.3" fill="#ffffff"/>'
)

svg.append(
    f'<circle cx="{hero_x + 8}" '
    f'cy="{hero_y + 4}" '
    f'r="1.3" fill="#ffffff"/>'
)

# Coding particles
symbols = [
    "&lt;/&gt;",
    "{ }",
    "01",
    "git",
    "*",
]

random.seed(42)

for _ in range(14):

    x = random.randint(60, 930)
    y = random.randint(80, 230)

    symbol = random.choice(symbols)

    color = random.choice([
        ACCENT,
        PURPLE,
        "#39d353",
    ])

    duration = random.randint(3, 6)

    svg.append(
        f'''
<text x="{x}" y="{y}"
      fill="{color}"
      opacity="0.35"
      font-family="monospace"
      font-size="10">
    {symbol}
    <animate
        attributeName="opacity"
        values="0.15;0.7;0.15"
        dur="{duration}s"
        repeatCount="indefinite"/>
</text>
'''
    )

# Bottom progress background
svg.append(
    f'<rect x="40" y="245" '
    f'width="920" height="5" '
    f'rx="3" fill="{GRID_EMPTY}"/>'
)

# Animated progress
svg.append(
    f'''
<rect x="40" y="245"
      width="650"
      height="5"
      rx="3"
      fill="{ACCENT}">
    <animate
        attributeName="width"
        values="100;650;100"
        dur="8s"
        repeatCount="indefinite"/>
</rect>
'''
)

# Footer
now = datetime.now().strftime("%d %b %Y")

svg.append(
    f'<text x="40" y="280" '
    f'fill="{MUTED}" '
    f'font-family="Arial, sans-serif" '
    f'font-size="11">'
    f'Last generated: {escape(now)}'
    f'</text>'
)

svg.append(
    f'<text x="960" y="280" '
    f'text-anchor="end" '
    f'fill="{PURPLE}" '
    f'font-family="monospace" '
    f'font-size="11">'
    f'@{escape(USERNAME)}'
    f'</text>'
)

svg.append("</svg>")

# Save directly in repository root
output_file = "developer-journey.svg"

with open(
    output_file,
    "w",
    encoding="utf-8",
) as file:
    file.write("\n".join(svg))

print(f"Developer Journey generated: {output_file}")
