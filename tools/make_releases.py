"""Write releases.json from the published release manifests: build, size, date and notes
for each plug-in that is out. The product pages and changes.html read it.

Re-run after every publish, or when a plug-in comes out (add it to PRODUCTS):
    python tools/make_releases.py
Needs the GitHub CLI (gh). Drafts and the fixed <id>-latest releases are skipped.
"""
import json
import os
import re
import subprocess

REPO = "SonnySSSSSSS/audiocitra-releases"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# release id -> (site page id, display name)
PRODUCTS = {"spanda": ("spanda", "Spanda"), "akasa": ("akasa", "Ākāśa"), "acfree": ("tula", "Tulā")}


def gh(*args):
    return subprocess.check_output(["gh", *args], text=True, encoding="utf-8")


def clean(notes):
    """Drop a leading "Name alpha 12 (build 34):" so the public text doesn't carry internal build words."""
    text = re.sub(r"^\s*\S+\s+(?:alpha|build)\s+\S+(?:\s+\(build\s+\d+\))?:\s*", "", notes or "", flags=re.I).strip()
    return text[:1].upper() + text[1:]


def main():
    rows = json.loads(gh("release", "list", "-R", REPO, "--limit", "200", "--json", "tagName,publishedAt,isDraft"))
    out = {page: {"name": name, "releases": []} for page, name in PRODUCTS.values()}
    for row in rows:
        tag = row["tagName"]
        rid = tag.split("-")[0]
        if row["isDraft"] or tag.endswith("-latest") or rid not in PRODUCTS:
            continue
        m = json.loads(gh("release", "download", tag, "-R", REPO, "-p", "manifest.json", "-O", "-"))
        out[PRODUCTS[rid][0]]["releases"].append({"date": row["publishedAt"][:10], "build": m["build"], "size": m["size"], "notes": clean(m.get("notes"))})
    for p in out.values():
        p["releases"].sort(key=lambda r: r["build"], reverse=True)
    with open(os.path.join(ROOT, "releases.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print({k: len(v["releases"]) for k, v in out.items()})


if __name__ == "__main__":
    main()
