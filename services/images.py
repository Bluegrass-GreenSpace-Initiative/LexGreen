# services/images.py
import os, re
from functools import lru_cache
from flask import current_app, url_for

_SLUG_RE = re.compile(r"[^a-z0-9]+")

def slugify_title(s: str) -> str:
    s = (s or "").strip().lower()
    return _SLUG_RE.sub("-", s).strip("-")

@lru_cache(maxsize=256)
def image_url_for_tree(common_name: str = "", latin_name: str = "", explicit: str | None = None) -> str:
    """
    Resolve a leaf image URL for a tree. If `explicit` is provided (relative to static/), use it.
    Otherwise, try a slug from common name, then latin name, across common extensions.
    Returns a static URL or a fallback.
    """
    static_root = current_app.static_folder
    subdir = "images/morphology"

    if explicit:
        rel = explicit if not explicit.startswith("/") else explicit.lstrip("/")
        p = os.path.join(static_root, rel)
        if os.path.exists(p):
            return url_for("static", filename=rel)

    candidates = []
    for base in filter(None, [slugify_title(common_name), slugify_title(latin_name)]):
        for ext in ("jpg", "jpeg", "png", "webp", "svg"):
            candidates.append(f"{subdir}/{base}.{ext}")

    for rel in candidates:
        if os.path.exists(os.path.join(static_root, rel)):
            return url_for("static", filename=rel)

    # Fallback placeholder you provide
    return url_for("static", filename=f"{subdir}/_fallback.svg")
