"""Builds dark_mode.svg / light_mode.svg for README.md. Run: python3 build.py"""

import calendar
import json
import os
import subprocess
import urllib.request
from datetime import date
from html import escape

USER = "RazorTheFolf"

ART = [  # from ~/.config/motd.sh
    "⠀⠀⠀⠀⠠⣾⣿⣦⣀⠀⠀⠠⣴⣦⣄⡀⠀⠀⠀",
    "⠀⠀⠀⠀⢸⣿⣿⣿⣿⡇⢀⣾⣿⣿⣿⣷⠀⠀⠀",
    "⠀⣀⣀⠀⠸⣿⣿⣿⣿⡇⢸⣿⣿⣿⣿⠃⠀⠀⠀",
    "⣼⣿⣿⣷⡄⠘⠿⠿⠟⠁⠘⢿⣿⡿⠋⠀⢀⡀⠀",
    "⢿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⣿⣿⣆",
    "⠘⢿⣿⣿⡿⠀⣀⣴⣶⣶⣦⣀⠀⠀⣿⣿⣿⣿⡟",
    "⠀⠀⠉⠉⢠⣾⣿⣿⣿⣿⣿⣿⣦⡀⣿⣿⣿⡟⠀",
    "⠀⠀⠀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡌⠉⠁⠀⠀",
    "⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⠀⠀⠀",
    "⠀⠀⠘⠿⢿⣿⠿⠿⠿⠿⠿⣿⣿⣿⠇⠀⠀⠀⠀",
]
# One per paw row, last one repeats, same as the motd
STRIPES = ["#61bb46", "#61bb46", "#fdb827", "#fdb827", "#f5821f", "#e03a3e", "#e03a3e", "#963d97", "#009ddc"]
# (x, y) of each braille bit in its 2x4 cell, in Unicode bit order
BRAILLE_DOTS = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (0, 3), (1, 3)]

THEMES = {
    "dark_mode.svg": dict(bg="#161b22", text="#c9d1d9", key="#ffa657", value="#a5d6ff", dots="#616e7f"),
    "light_mode.svg": dict(bg="#f6f8fa", text="#24292f", key="#953800", value="#0a3069", dots="#c2cfde"),
}
CH, LH, PAD = 9.6, 20, 20  # 16px monospace char width, line height, card padding
MIN_DOTS = 4


def gql(query, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        json.dumps({"query": query}).encode(),
        {"Authorization": f"bearer {token}"},
    )
    res = json.load(urllib.request.urlopen(req))
    if "errors" in res:
        raise SystemExit(res["errors"])
    return res["data"]["user"]


def stats():
    token = os.environ.get("GITHUB_TOKEN") or subprocess.check_output(["gh", "auth", "token"], text=True).strip()
    # shortcut: stars only cover the first 100 repos, paginate if that is ever outgrown
    u = gql(
        f'''{{ user(login: "{USER}") {{ createdAt followers {{ totalCount }}
        repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100) {{ totalCount nodes {{ stargazerCount }} }}
        contributionsCollection {{ contributionYears }} }} }}''',
        token,
    )
    years = " ".join(
        f'y{y}: contributionsCollection(from: "{y}-01-01T00:00:00Z", to: "{y}-12-31T23:59:59Z") {{ totalCommitContributions }}'
        for y in u["contributionsCollection"]["contributionYears"]
    )
    commits = sum(v["totalCommitContributions"] for v in gql(f'{{ user(login: "{USER}") {{ {years} }} }}', token).values())
    return dict(
        uptime=age(date.fromisoformat(u["createdAt"][:10]), date.today()),
        repos=str(u["repositories"]["totalCount"]),
        stars=str(sum(r["stargazerCount"] for r in u["repositories"]["nodes"])),
        commits=f"{commits:,}",
        followers=str(u["followers"]["totalCount"]),
    )


def age(start, today):
    def plus_months(n):  # day clamped to the month's length: Oct 31 + 4 months -> Feb 28
        yr, mo = divmod(start.month - 1 + n, 12)
        return date(start.year + yr, mo + 1, min(start.day, calendar.monthrange(start.year + yr, mo + 1)[1]))

    months = (today.year - start.year) * 12 + today.month - start.month
    if plus_months(months) > today:
        months -= 1
    y, m = divmod(months, 12)
    d = (today - plus_months(months)).days
    return ", ".join(f"{n} {unit}{'s' * (n != 1)}" for n, unit in ((y, "year"), (m, "month"), (d, "day")))


assert age(date(2020, 10, 11), date(2026, 11, 26)) == "6 years, 1 month, 15 days"
assert age(date(2020, 10, 31), date(2026, 3, 1)) == "5 years, 4 months, 1 day"


def info(s):
    """(key, value) rows; key None = section header, "" = blank, a list = several pairs on one line."""
    return [
        (None, "razor@folf"),
        ("OS", "macOS, Linux"),
        ("Uptime", s["uptime"]),
        ("Host", "IPSSI - BTS SIO SLAM (2025 - 2027)"),
        ("Kernel", "Software Engineer, IoT tinkerer"),
        ("Status", "Looking for an alternance (Web / IoT)"),
        ("", ""),
        ("Languages.Front", "TypeScript, React, React Native, Vue"),
        ("Languages.Back", "Node.js, Go, PHP, Java, C++"),
        ("Languages.Real", "French, English, Romanian"),
        ("Data", "PostgreSQL, MongoDB, MariaDB, Redis"),
        ("Ops", "Docker, GitHub Actions, n8n, Prisma"),
        ("", ""),
        (None, "IoT"),
        ("Into", "Microcontrollers, sensors, home automation"),
        ("Learning", "C++ on ESP32, MQTT, Home Assistant"),
        ("Goal", "Wire real-world devices to the web"),
        ("", ""),
        (None, "Razor"),
        ("Species", "Folf (fox x wolf)"),
        ("Shell", "zsh, greeted by a rainbow paw"),
        ([("Fun side", "raz0r.fr"), ("Pro side", "me.raz0r.fr")], None),
        ("", ""),
        (None, "Experience"),
        ("Furalure Events", "Full-Stack Intern, Apr - Jun 2026"),
        ("Built", "PAM: OIDC, multi-admin quorum"),
        ("", ""),
        (None, "Contact"),
        ("Email", "contact@raz0r.fr"),
        ("", ""),
        (None, "GitHub Stats"),
        ([("Repos", s["repos"]), ("Stars", s["stars"])], None),
        ([("Commits", s["commits"]), ("Followers", s["followers"])], None),
    ]


def pairs_of(key, value):
    return key if isinstance(key, list) else [(key, value)]


def min_width(rows):
    """Narrowest info column where every row still gets MIN_DOTS of leader."""
    need = [len(v) + 6 for k, v in rows if k is None]
    for k, v in rows:
        if k:
            pairs = pairs_of(k, v)
            widest = max(len(pk) + len(pv) + 4 + MIN_DOTS for pk, pv in pairs)
            need.append(2 + 3 * (len(pairs) - 1) + widest * len(pairs))
    return max(need)


def info_line(key, value, width):
    if key is None:
        return [("text", f"- {value} " + "-" * (width - len(value) - 3))]
    if key == "":
        return [("text", "")]
    pairs = pairs_of(key, value)
    room = width - 2 - 3 * (len(pairs) - 1)  # minus ". " and " | " separators
    spans = [("text", ". ")]
    for i, (k, v) in enumerate(pairs):
        w = room // len(pairs) + (room % len(pairs) if i == len(pairs) - 1 else 0)
        dots = "." * (w - len(k) - len(v) - 4)
        spans += [("text", " | ")] * (i > 0) + [("key", k), ("text", ": "), ("dots", dots), ("text", " "), ("value", v)]
    return spans


def build(c, rows):
    width = min_width(rows)
    pitch = len(rows) * LH * 0.9 / (len(ART) * 4)  # paw fills 90% of the info height
    art_px = max(map(len, ART)) * 2 * pitch
    text_x = PAD + art_px + 3 * CH
    w, h = int(text_x + width * CH + PAD), len(rows) * LH + 2 * PAD
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" '
        f'width="{w}px" height="{h}px" font-size="16px">',
        f"<style>text,tspan{{white-space:pre}} .key{{fill:{c['key']}}} .value{{fill:{c['value']}}} .dots{{fill:{c['dots']}}}</style>",
        f'<rect width="{w}px" height="{h}px" fill="{c["bg"]}" rx="15"/>',
    ]
    # Drawn as circles rather than text so no font can stretch the paw
    top = PAD + (len(rows) * LH - len(ART) * 4 * pitch) / 2
    for row, line in enumerate(ART):
        out.append(f'<g fill="{STRIPES[min(row, len(STRIPES) - 1)]}">')
        for col, char in enumerate(line):
            bits = ord(char) - 0x2800
            out += [
                f'<circle cx="{PAD + (col * 2 + dx + 0.5) * pitch:.1f}" cy="{top + (row * 4 + dy + 0.5) * pitch:.1f}" r="{pitch * 0.42:.1f}"/>'
                for bit, (dx, dy) in enumerate(BRAILLE_DOTS)
                if bits >> bit & 1
            ]
        out.append("</g>")
    out.append(f'<text fill="{c["text"]}">')
    for i, (k, v) in enumerate(rows):
        spans = "".join(
            escape(t) if cls == "text" else f'<tspan class="{cls}">{escape(t)}</tspan>' for cls, t in info_line(k, v, width)
        )
        out.append(f'<tspan x="{text_x:.0f}" y="{PAD + 10 + i * LH}">{spans}</tspan>')
    out += ["</text>", "</svg>"]
    return "\n".join(out)


if __name__ == "__main__":
    rows = info(stats())
    for name, colors in THEMES.items():
        open(name, "w").write(build(colors, rows))
