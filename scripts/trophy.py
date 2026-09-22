"""Downloads the trophy card and converts it to grayscale (none of the service themes is black and white)."""

import re
import sys
import urllib.request

URL = (
    "https://github-trophies.vercel.app/?username=mateusands&theme=gitdimmed"
    "&no-frame=true&row=1&column=7&margin-w=12"
    "&title=MultiLanguage,LongTimeUser,Commits,PullRequest,Repositories,Stars,Followers"
)
OUT = sys.argv[1] if len(sys.argv) > 1 else "profile/trophy.svg"

with urllib.request.urlopen(URL, timeout=60) as res:
    svg = res.read().decode()

if "<svg" not in svg:
    sys.exit("unexpected response from the trophy service")

gray = (
    '<defs><filter id="gs"><feColorMatrix type="saturate" values="0"/></filter></defs>'
    '<g filter="url(#gs)">'
)
svg = re.sub(r"(<svg\b[^>]*>)", r"\1" + gray, svg, count=1)
svg = svg[: svg.rstrip().rfind("</svg>")] + "</g></svg>\n"

with open(OUT, "w") as f:
    f.write(svg)
