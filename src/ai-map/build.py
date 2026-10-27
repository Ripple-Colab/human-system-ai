"""Assemble index.html from template.html, the dataset, logos and faces."""
import base64, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(HERE, "data.checked.json")
if not os.path.exists(src) or "--draft" in sys.argv:
    src = os.path.join(HERE, "data.json")
data = json.load(open(src))

# Structural overrides kept out of the fact-checked dataset
RENAMES = {
    "meta": {"name": "Facebook", "logo": "facebook", "rename": [["2021-10-28", "Meta", "meta"]]},
    "x": {"name": "Twitter", "logo": None, "mono": "Tw", "rename": [["2023-07-24", "X", "x"]]},
}
HOMES = {"tml": [0.08, 0.34], "ssi": [-0.24, 0.3], "huggingface": [-0.66, -0.6]}
for o in data["orgs"]:
    if o["id"] in RENAMES:
        o.update(RENAMES[o["id"]])
    if o["id"] in HOMES:
        o["home"] = HOMES[o["id"]]

logos = {}
for f in os.listdir(os.path.join(HERE, "logos")):
    if f.endswith(".svg"):
        svg = open(os.path.join(HERE, "logos", f)).read()
        m = re.search(r'<path d="([^"]+)"', svg)
        if m:
            logos[f[:-4]] = m.group(1)

faces = {}
fdir = os.path.join(HERE, "faces")
if os.path.isdir(fdir):
    for f in sorted(os.listdir(fdir)):
        if f.endswith(".jpg"):
            b = base64.b64encode(open(os.path.join(fdir, f), "rb").read()).decode()
            faces[f[:-4]] = "data:image/jpeg;base64," + b

def load(name, default):
    f = os.path.join(HERE, name)
    if "--sample" in sys.argv:
        f = os.path.join(HERE, "sample." + name) if os.path.exists(os.path.join(HERE, "sample." + name)) else f
    return json.load(open(f)) if os.path.exists(f) else default

releases = load("releases.json", [])
values = load("values.json", {})
page = open(os.path.join(HERE, "template.html")).read()
page = page.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False))
page = page.replace("/*__LOGOS__*/{}", json.dumps(logos))
page = page.replace("/*__FACES__*/{}", json.dumps(faces))
page = page.replace("/*__RELEASES__*/[]", json.dumps(releases, ensure_ascii=False))
page = page.replace("/*__VALUES__*/{}", json.dumps(values, ensure_ascii=False))
logo_b64 = base64.b64encode(open(os.path.join(HERE, "brand", "logo-80.png"), "rb").read()).decode()
page = page.replace('/*__RCLOGO__*/""', json.dumps("data:image/png;base64," + logo_b64))
cp = os.path.join(fdir, "credits.json")
credits = {k: v for k, v in (json.load(open(cp)) if os.path.exists(cp) else {}).items() if k in faces}
page = page.replace("/*__CREDITS__*/{}", json.dumps(credits, ensure_ascii=False))
open(os.path.join(HERE, "index.html"), "w").write(page)
print(f"built from {os.path.basename(src)}: {len(data['people'])} people, {len(data['orgs'])} orgs, "
      f"{len(data['links'])} links, {len(data['events'])} events, {len(releases)} releases, {len(values)} valued, {len(logos)} logos, {len(faces)} faces, "
      f"{len(page)//1024} KB")

# Local test copy wrapped in a skeleton like the one the artifact host adds
open(os.path.join(HERE, "index.test.html"), "w").write(
    '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
    '<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)}'
    'body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style></head><body>' + page + '</body></html>')

# Public site: python3 build.py --site <public dir>
# Writes <public>/ai/index.html as a full document that serves its own fonts and D3, plus the favicon, fonts and D3.
if "--site" in sys.argv:
    out = os.path.abspath(sys.argv[sys.argv.index("--site") + 1])
    os.makedirs(os.path.join(out, "ai"), exist_ok=True)
    cut = page.index("</style>") + len("</style>")
    head, body = page[:cut], page[cut:]
    head = re.sub(r'<link rel="preconnect"[^>]*>\s*', "", head)
    head = re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>', """<style>
@font-face { font-family: "Josefin Sans"; src: url("/fonts/JosefinSans.woff2") format("woff2"); font-weight: 100 700; font-display: swap; }
@font-face { font-family: "Karla"; src: url("/fonts/Karla.woff2") format("woff2"); font-weight: 200 800; font-display: swap; }
</style>""", head)
    head = head.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
    body = body.replace("https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js", "/vendor/d3-7.9.0.min.js")
    desc = ("An animated map of who worked where, who paid whom and who fell out in AI, "
            "2012 to 2026. Every tie, event and value links to its source.")
    site = f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
{head}
<meta name="description" content="{desc}">
<link rel="canonical" href="https://lab.ripplecolab.com/ai/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Ripple CoLab">
<meta property="og:title" content="The Human System of AI">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="https://lab.ripplecolab.com/ai/">
<meta property="og:image" content="https://lab.ripplecolab.com/ai/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="/favicon.png">
<script defer src="/_vercel/insights/script.js"></script>
</head>
<body>
{body}
</body>
</html>
"""
    open(os.path.join(out, "ai", "index.html"), "w").write(site)
    print("site page:", os.path.join(out, "ai", "index.html"), f"{len(site)//1024} KB")
