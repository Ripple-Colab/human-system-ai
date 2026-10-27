"""Fetch each person's lead Wikipedia photo, crop to a square face, and record the credit.

Needs network access to en.wikipedia.org, upload.wikimedia.org and commons.wikimedia.org.
Skips non-free (fair-use) images; those people keep their initials.
"""
import io, json, os, re, sys, urllib.parse, urllib.request
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "RippleCoLab-AI-map/1.0 (interactive explainer; one-off fetch)"}
src = os.path.join(HERE, "data.checked.json")
data = json.load(open(src if os.path.exists(src) else os.path.join(HERE, "data.json")))
os.makedirs(os.path.join(HERE, "faces"), exist_ok=True)
credits_path = os.path.join(HERE, "faces", "credits.json")
credits = json.load(open(credits_path)) if os.path.exists(credits_path) else {}

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
        return r.read()

def strip(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()

for p in data["people"]:
    out = os.path.join(HERE, "faces", p["id"] + ".jpg")
    if os.path.exists(out) and "--force" not in sys.argv:
        continue
    try:
        s = json.loads(get("https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(p["wiki"])))
        orig = (s.get("originalimage") or {}).get("source")
        thumb = (s.get("thumbnail") or {}).get("source")
        if not orig or not thumb:
            print("no image:", p["id"]); continue
        fname = urllib.parse.unquote(orig.rsplit("/", 1)[-1])
        meta = json.loads(get("https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo"
                              "&iiprop=extmetadata&titles=" + urllib.parse.quote("File:" + fname)))
        pages = meta["query"]["pages"]
        info = next(iter(pages.values())).get("imageinfo")
        if not info:
            print("not on Commons (likely non-free), skipped:", p["id"]); continue
        em = info[0]["extmetadata"]
        lic = strip(em.get("LicenseShortName", {}).get("value", ""))
        if re.search(r"fair use|non-free", lic, re.I):
            print("non-free, skipped:", p["id"]); continue
        big = re.sub(r"/\d+px-", "/400px-", thumb)
        img = Image.open(io.BytesIO(get(big))).convert("RGB")
        w, h = img.size; side = min(w, h)
        left = (w - side) // 2; top = int((h - side) * 0.18)
        img = img.crop((left, top, left + side, top + side)).resize((128, 128), Image.LANCZOS)
        img.save(out, "JPEG", quality=80, optimize=True, progressive=True)
        credits[p["id"]] = {"artist": strip(em.get("Artist", {}).get("value", ""))[:120], "license": lic,
                            "page": "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(fname.replace(" ", "_"))}
        print("ok:", p["id"], lic)
    except Exception as e:
        print("failed:", p["id"], type(e).__name__, str(e)[:80])

json.dump(credits, open(credits_path, "w"), indent=1, ensure_ascii=False)
