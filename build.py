"""Builds dark_mode.svg / light_mode.svg, the neofetch-style card in README.md. Run: python3 build.py"""
import calendar
import json
import os
import subprocess
import urllib.request
from datetime import date
from html import escape

ART = [  # braille paw from ~/.config/motd.sh
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
# Apple-logo stripes, one color per paw row, like the motd
STRIPES = ["#61bb46", "#61bb46", "#fdb827", "#fdb827", "#f5821f", "#e03a3e", "#e03a3e", "#963d97", "#009ddc", "#009ddc"]
DOT_PITCH = 12  # px between paw dots; the paw is drawn as circles so no font can stretch it
# (x, y) of each braille bit in its 2x4 cell, in Unicode bit order (dots 1-8)
BRAILLE_DOTS = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (0, 3), (1, 3)]

WIDTH = 60  # info column width in characters
USER = "RazorTheFolf"


def gql(query, token):
    req = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": query}).encode(),
                                 {"Authorization": f"bearer {token}"})
    res = json.load(urllib.request.urlopen(req))
    if "errors" in res:
        raise SystemExit(res["errors"])
    return res["data"]["user"]


def stats():
    """Public GitHub numbers for USER. Token from $GITHUB_TOKEN (the Action) or the gh CLI (local runs)."""
    token = os.environ.get("GITHUB_TOKEN") or subprocess.check_output(["gh", "auth", "token"], text=True).strip()
    # shortcut: stars only cover the first 100 repos, paginate if that is ever outgrown
    u = gql(f'''{{ user(login: "{USER}") {{ createdAt followers {{ totalCount }}
        repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100) {{ totalCount nodes {{ stargazerCount }} }}
        contributionsCollection {{ contributionYears }} }} }}''', token)
    years = " ".join(f'y{y}: contributionsCollection(from: "{y}-01-01T00:00:00Z", to: "{y}-12-31T23:59:59Z") '
                     f'{{ totalCommitContributions }}' for y in u["contributionsCollection"]["contributionYears"])
    commits = sum(v["totalCommitContributions"] for v in gql(f'{{ user(login: "{USER}") {{ {years} }} }}', token).values())
    return dict(
        uptime=age(date.fromisoformat(u["createdAt"][:10]), date.today()),
        repos=str(u["repositories"]["totalCount"]),
        stars=str(sum(r["stargazerCount"] for r in u["repositories"]["nodes"])),
        commits=f"{commits:,}",
        followers=str(u["followers"]["totalCount"]),
    )


def age(start, today):
    """'6 years, 1 month, 15 days' between two dates."""
    def plus_months(n):  # start + n months, day clamped to the month's length (Oct 31 + 4 -> Feb 28)
        yr, mo = divmod(start.month - 1 + n, 12)
        return date(start.year + yr, mo + 1, min(start.day, calendar.monthrange(start.year + yr, mo + 1)[1]))

    months = (today.year - start.year) * 12 + today.month - start.month
    if plus_months(months) > today:
        months -= 1
    d = (today - plus_months(months)).days
    y, m = divmod(months, 12)
    return ", ".join(f"{n} {unit}{'s' * (n != 1)}" for n, unit in ((y, "year"), (m, "month"), (d, "day")))


assert age(date(2020, 10, 11), date(2026, 11, 26)) == "6 years, 1 month, 15 days"
assert age(date(2020, 10, 31), date(2026, 3, 1)) == "5 years, 4 months, 1 day"


def info(s):
    """Card rows: (key, value); key None = section header, "" = blank line, a list = several pairs on one line."""
    return [
        (None, "raoul@raz0r"),
        ("OS", "macOS, Linux"),
        ("Uptime", s["uptime"]),
        ("Host", "IPSSI - BTS SIO SLAM (2025 - 2027)"),
        ("Kernel", "Full-Stack Developer"),
        ("Status", "Looking for an alternance (1 wk / 1 wk)"),
        ("", ""),
        ("Languages.Front", "TypeScript, React, React Native, Vue"),
        ("Languages.Back", "Node.js, Go, PHP, Java, C++"),
        ("Languages.Real", "French, English (C1), Romanian (A2)"),
        ("Data", "PostgreSQL, MongoDB, MariaDB, Redis"),
        ("Ops", "Docker, GitHub Actions, n8n, Prisma"),
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
        ("Email", "raoul.iftode.pro@gmail.com"),
        ([("LinkedIn", "raoul-iftode"), ("City", "Paris")], None),
        ("", ""),
        (None, "GitHub Stats"),
        ([("Repos", s["repos"]), ("Stars", s["stars"])], None),
        ([("Commits", s["commits"]), ("Followers", s["followers"])], None),
    ]

THEMES = {
    "dark_mode.svg": dict(bg="#161b22", text="#c9d1d9", key="#ffa657", value="#a5d6ff", dots="#616e7f"),
    "light_mode.svg": dict(bg="#f6f8fa", text="#24292f", key="#953800", value="#0a3069", dots="#c2cfde"),
}


def info_line(key, value):
    if key is None:  # header: "- Contact -------"
        return [("text", f"- {value} " + "-" * (WIDTH - len(value) - 3))]
    if key == "":
        return [("text", "")]
    pairs = key if isinstance(key, list) else [(key, value)]
    room = WIDTH - 2 - 3 * (len(pairs) - 1)  # after ". " and the " | " separators
    spans = [("text", ". ")]
    for i, (k, v) in enumerate(pairs):
        w = room // len(pairs) + (room % len(pairs) if i == len(pairs) - 1 else 0)  # last pair takes the remainder
        dots = w - len(k) - len(v) - 4
        assert dots >= 2, f"line too long: {k}: {v}"
        spans += [("text", " | ")] * (i > 0) + [("key", k), ("text", ": "), ("dots", "." * dots), ("text", " "), ("value", v)]
    return spans


def build(c, lines):
    ch, lh = 9.6, 20  # char width / line height for 16px monospace
    rows = len(lines)
    art_px = max(map(len, ART)) * 2 * DOT_PITCH  # each braille char is 2 dots wide, 4 tall
    art_w = art_px / ch + 3  # in info-sized chars, +3 for the gap
    w, h = int((art_w + WIDTH) * ch + 40), rows * lh + 40
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" '
        f'width="{w}px" height="{h}px" font-size="16px">',
        f"<style>text,tspan{{white-space:pre}} .key{{fill:{c['key']}}} .value{{fill:{c['value']}}} .dots{{fill:{c['dots']}}}</style>",
        f'<rect width="{w}px" height="{h}px" fill="{c["bg"]}" rx="15"/>',
    ]
    top = 20 + (rows * lh - len(ART) * 4 * DOT_PITCH) / 2  # vertically centered beside the info
    for row, (line, stripe) in enumerate(zip(ART, STRIPES)):
        out.append(f'<g fill="{stripe}">')
        for col, char in enumerate(line):
            bits = ord(char) - 0x2800
            out += [f'<circle cx="{20 + (col * 2 + dx + 0.5) * DOT_PITCH:.1f}" cy="{top + (row * 4 + dy + 0.5) * DOT_PITCH:.1f}" '
                    f'r="{DOT_PITCH * 0.42:.1f}"/>' for bit, (dx, dy) in enumerate(BRAILLE_DOTS) if bits >> bit & 1]
        out.append("</g>")
    out.append(f'<text x="{20 + art_w * ch:.0f}" y="30" fill="{c["text"]}">')
    for i, (k, v) in enumerate(lines):
        spans = "".join(escape(t) if cls == "text" else f'<tspan class="{cls}">{escape(t)}</tspan>' for cls, t in info_line(k, v))
        out.append(f'<tspan x="{20 + art_w * ch:.0f}" y="{30 + i * lh}">{spans}</tspan>')
    out += ["</text>", "</svg>"]
    return "\n".join(out)


if __name__ == "__main__":
    rows = info(stats())
    for name, colors in THEMES.items():
        open(name, "w").write(build(colors, rows))
