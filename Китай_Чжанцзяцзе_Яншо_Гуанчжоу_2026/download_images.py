# -*- coding: utf-8 -*-
"""Download a few Wikimedia Commons photos per attraction (thumbnails ~520px)."""
import json, pathlib, time, urllib.parse, urllib.request

BASE = pathlib.Path(__file__).parent
IMG = BASE / "images"
IMG.mkdir(exist_ok=True)
UA = "TravelItineraryBuilder/1.0 (personal trip planning; contact local)"

# prefix -> (search query, how many to keep)
JOBS = {
    # Zhangjiajie
    "zjj_yuanjiajie": ("Wulingyuan", 5),
    "zjj_tianzi":     ("Tianzi Mountain Zhangjiajie", 4),
    "zjj_bailong":    ("Bailong Elevator Zhangjiajie", 4),
    "zjj_goldenwhip": ("Golden Whip Stream", 3),
    "zjj_tianmen":    ("Tianmen Mountain Zhangjiajie", 5),
    "zjj_glassbridge":("Zhangjiajie Grand Canyon Glass Bridge", 4),
    # Furong Town (Xiangxi)
    "furong":         ("Furong Town Yongshun waterfall", 4),
    # Yangshuo / Guilin
    "ys_lijiang":     ("Li River Xingping Guilin", 5),
    "ys_yulong":      ("Yulong River Yangshuo bamboo raft", 4),
    "ys_moonhill":    ("Moon Hill Yangshuo", 4),
    "ys_xianggong":   ("Xianggong", 4),
    "ys_impression":  ("Impression Sanjie Liu Yangshuo show", 4),
    "ys_weststreet":  ("West Street Yangshuo", 5),
    # Guangzhou
    "gz_canton":      ("Canton Tower Guangzhou", 3),
    "gz_shamian":     ("Shamian Island Guangzhou", 3),
    "gz_chenclan":    ("Chen Clan Ancestral Hall Guangzhou", 2),
    "gz_pearlriver":  ("Pearl River Guangzhou night", 3),
    "gz_beijinglu":   ("Beijing Road Guangzhou", 3),
    # Shenzhen
    "sz_pingan":      ("Ping An Finance Centre Shenzhen", 2),
    "sz_skyline":     ("Shenzhen skyline Futian", 2),
    "sz_civic":       ("Shenzhen Civic Center", 1),
    "sz_bay":         ("Shenzhen Bay Park", 1),
    "sz_seaworld":    ("Sea World Shekou Shenzhen", 1),
    "sz_huaqiangbei": ("Huaqiangbei Shenzhen electronics market", 1),
    "sz_dongmen":     ("Dongmen Pedestrian Street Shenzhen", 1),
}

API = "https://commons.wikimedia.org/w/api.php"
HDRS = {
    "User-Agent": UA,
    "Accept": "image/jpeg,image/png,*/*",
    "Referer": "https://commons.wikimedia.org/",
}

def get(url, timeout=60, tries=6):
    """GET with polite exponential backoff on 429/5xx."""
    delay = 2.0
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=HDRS)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < tries - 1:
                time.sleep(delay); delay *= 1.8; continue
            raise
    raise RuntimeError("exhausted retries")

def search_images(query, limit):
    params = {
        "action": "query", "format": "json",
        "generator": "search", "gsrsearch": query,
        "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime",
        "iiurlwidth": "520",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    data = json.loads(get(url, timeout=40).decode("utf-8"))
    pages = data.get("query", {}).get("pages", {})
    # keep search order
    pages = sorted(pages.values(), key=lambda p: p.get("index", 99))
    out = []
    for p in pages:
        ii = p.get("imageinfo", [{}])[0]
        thumb = ii.get("thumburl")
        mime = ii.get("mime", "")
        if thumb and ("jpeg" in mime or "png" in mime):
            out.append(thumb)
    return out

def have(prefix, idx):
    for ext in (".jpg", ".png"):
        if (IMG / f"{prefix}_{idx}{ext}").exists():
            return True
    return False

def run():
  for prefix, (query, keep) in JOBS.items():
    # how many already on disk?
    existing = sum(1 for i in range(1, keep + 1) if have(prefix, i))
    if existing >= keep:
        print(f"SKIP {prefix}: already {existing}/{keep}")
        continue
    try:
        urls = search_images(query, keep + 5)
    except Exception as e:
        print("SEARCH FAIL", prefix, e); time.sleep(3); continue
    n = existing
    ui = 0
    while n < keep and ui < len(urls):
        u = urls[ui]; ui += 1
        idx = n + 1
        if have(prefix, idx):
            n += 1; continue
        ext = ".png" if ".png" in u.lower() else ".jpg"
        dest = IMG / f"{prefix}_{idx}{ext}"
        try:
            dest.write_bytes(get(u))
            print("OK", dest.name, f"({dest.stat().st_size//1024} KB)")
            n += 1
        except Exception as e:
            print("DL FAIL", prefix, idx, e)
        time.sleep(1.2)
    if n < keep:
        print(f"  !! {prefix}: got {n}/{keep}")
  print("DONE")

if __name__ == "__main__":
    run()
