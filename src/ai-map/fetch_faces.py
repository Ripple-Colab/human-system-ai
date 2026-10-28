"""Fetch each person's lead Wikipedia photo, crop to a square face, and record the credit.

Needs network access to en.wikipedia.org, upload.wikimedia.org and commons.wikimedia.org.
Skips non-free (fair-use) images; those people keep their initials.
"""
import io, json, os, re, sys, time, urllib.parse, urllib.request
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "RippleCoLab-AI-map/1.0 (https://lab.ripplecolab.com/human-system-ai/; one-off portrait fetch)"}
src = os.path.join(HERE, "data.checked.json")
data = json.load(open(src if os.path.exists(src) else os.path.join(HERE, "data.json")))
os.makedirs(os.path.join(HERE, "faces"), exist_ok=True)
credits_path = os.path.join(HERE, "faces", "credits.json")
credits = json.load(open(credits_path)) if os.path.exists(credits_path) else {}

def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == tries - 1:
                raise
            time.sleep(5 * (i + 1))

def strip(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()

for p in data["people"]:
    time.sleep(1)
    out = os.path.join(HERE, "faces", p["id"] + ".jpg")
    if os.path.exists(out) and p["id"] in credits and "--force" not in sys.argv:
        continue
    surname = p["name"].split()[-1].lower()
    if surname not in p["wiki"].lower():
        print("no article of their own, skipped:", p["id"], flush=True)
        if os.path.exists(out):
            os.remove(out)
        continue
    try:
        s = json.loads(get("https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(p["wiki"])))
        if surname not in (s.get("title") or "").lower():
            print("link redirects away from the person, skipped:", p["id"], flush=True); continue
        orig = ((s.get("originalimage") or {}).get("source") or "").split("?")[0]
        thumb = (s.get("thumbnail") or {}).get("source")
        if not orig or not thumb:
            print("no image:", p["id"], flush=True); continue
        fname = re.sub(r"^\d+px-", "", urllib.parse.unquote(orig.rsplit("/", 1)[-1]))  # originals can come back pre-sized
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
        big = thumb  # Wikipedia's own thumbnail, already a standard size
        img = Image.open(io.BytesIO(get(big))).convert("RGB")
        w, h = img.size; side = min(w, h)
        left = (w - side) // 2; top = int((h - side) * 0.18)
        img = img.crop((left, top, left + side, top + side)).resize((128, 128), Image.LANCZOS)
        img.save(out, "JPEG", quality=80, optimize=True, progressive=True)
        credits[p["id"]] = {"artist": strip(em.get("Artist", {}).get("value", ""))[:120], "license": lic,
                            "page": "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(fname.replace(" ", "_"))}
        json.dump(credits, open(credits_path, "w"), indent=1, ensure_ascii=False)
        print("ok:", p["id"], lic, flush=True)
    except Exception as e:
        print("failed:", p["id"], type(e).__name__, str(e)[:80])

json.dump(credits, open(credits_path, "w"), indent=1, ensure_ascii=False)
