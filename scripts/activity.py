"""Gera profile/activity.svg: contribuições dos últimos 31 dias, em preto e branco."""

import json
import os
import sys
import urllib.request
from datetime import date

USER = os.environ.get("GH_USER", "mateusands")
TOKEN = os.environ["GITHUB_TOKEN"]
OUT = sys.argv[1] if len(sys.argv) > 1 else "profile/activity.svg"
DAYS = 31

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch():
    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as res:
        data = json.load(res)
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    return days[-DAYS:]


def render(days):
    W, H = 1200, 340
    left, right, top, bottom = 64, 32, 76, 52
    pw, ph = W - left - right, H - top - bottom
    counts = [d["contributionCount"] for d in days]
    peak = max(max(counts), 4)
    step = -(-peak // 4)
    ymax = step * 4

    def x(i):
        return left + i * pw / (len(days) - 1)

    def y(v):
        return top + ph - v * ph / ymax

    pts = [(x(i), y(c)) for i, c in enumerate(counts)]
    line = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    area = f"{left},{top + ph} {line} {left + pw},{top + ph}"

    mono = "ui-monospace,SFMono-Regular,'JetBrains Mono',Menlo,Consolas,monospace"
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{mono}">',
        '<defs><linearGradient id="a" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#fff" stop-opacity=".28"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="#0d0d0d" stroke="#262626"/>',
        f'<text x="{left}" y="44" font-size="18" font-weight="700" fill="#fff">atividade · últimos {DAYS} dias</text>',
        f'<text x="{W - right}" y="44" font-size="14" fill="#6b6b6b" text-anchor="end">{sum(counts)} contribuições</text>',
    ]
    for k in range(5):
        v = step * k
        gy = y(v)
        out.append(f'<line x1="{left}" y1="{gy:.1f}" x2="{left + pw}" y2="{gy:.1f}" stroke="#1f1f1f"/>')
        out.append(f'<text x="{left - 12}" y="{gy + 4:.1f}" font-size="11" fill="#6b6b6b" text-anchor="end">{v}</text>')
    for i, d in enumerate(days):
        if i % 3 == 0 or i == len(days) - 1:
            label = date.fromisoformat(d["date"]).strftime("%d/%m")
            out.append(f'<text x="{x(i):.1f}" y="{H - 22}" font-size="11" fill="#6b6b6b" text-anchor="middle">{label}</text>')
    out.append(f'<polygon points="{area}" fill="url(#a)"/>')
    out.append(f'<polyline points="{line}" fill="none" stroke="#fff" stroke-width="2" stroke-linejoin="round"/>')
    for (px, py), c in zip(pts, counts):
        fill = "#fff" if c else "#0d0d0d"
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="{fill}" stroke="#fff" stroke-width="1.5"/>')
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    with open(OUT, "w") as f:
        f.write(render(fetch()))
