#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
BASE_URL = "https://techkwon.github.io/brickbot-faq/"
FILES = ["index.html", "privacy.html", "404.html", "robots.txt", "sitemap.xml", "site.webmanifest", ".nojekyll"]
DIRS = ["assets", "data"]
FAQ_SCHEMA_MARKER = "<!-- FAQ_STRUCTURED_DATA -->"


def build_faq_schema() -> str:
    index = json.loads((ROOT / "data" / "index.json").read_text(encoding="utf-8"))
    daily = index.get("daily") or []
    if not daily:
        return ""
    latest_date = daily[0]["date"]
    data = json.loads((ROOT / "data" / "daily" / f"{latest_date}.json").read_text(encoding="utf-8"))
    entities = [
        {
            "@type": "Question",
            "name": faq["question"],
            "acceptedAnswer": {"@type": "Answer", "text": faq["answer"]},
        }
        for faq in data.get("faqs", [])
    ]
    if not entities:
        return ""
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "@id": f"{BASE_URL}#latest-faq",
        "url": BASE_URL,
        "name": f"{latest_date} 중등 강사진 FAQ",
        "datePublished": latest_date,
        "dateModified": data["generated_at"],
        "inLanguage": "ko-KR",
        "mainEntity": entities,
    }
    payload = json.dumps(schema, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/ld+json" id="faq-structured-data">{payload}</script>'


def inject_faq_schema() -> None:
    path = OUT / "index.html"
    text = path.read_text(encoding="utf-8")
    if FAQ_SCHEMA_MARKER not in text:
        raise RuntimeError("FAQ structured-data marker missing from index.html")
    path.write_text(text.replace(FAQ_SCHEMA_MARKER, build_faq_schema(), 1), encoding="utf-8")


def write_sitemap() -> None:
    index = json.loads((ROOT / "data" / "index.json").read_text(encoding="utf-8"))
    lastmod = str(index.get("updated_at") or "")[:10]
    lastmod_line = f"\n    <lastmod>{lastmod}</lastmod>" if lastmod else ""
    content = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{BASE_URL}</loc>{lastmod_line}
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>{BASE_URL}privacy.html</loc>
    <changefreq>monthly</changefreq>
    <priority>0.3</priority>
  </url>
</urlset>
'''
    (OUT / "sitemap.xml").write_text(content, encoding="utf-8")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for name in FILES:
        source = ROOT / name
        if source.exists():
            shutil.copy2(source, OUT / name)
    for name in DIRS:
        shutil.copytree(ROOT / name, OUT / name)
    inject_faq_schema()
    write_sitemap()
    print(f"prepared={OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
