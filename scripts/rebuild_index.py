#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAILY = ROOT / "data" / "daily"
INDEX = ROOT / "data" / "index.json"
SEARCH = ROOT / "data" / "search.json"


def main() -> int:
    DAILY.mkdir(parents=True, exist_ok=True)
    entries = []
    search_faqs = []
    for path in sorted(DAILY.glob("*.json"), reverse=True):
        data = json.loads(path.read_text(encoding="utf-8"))
        faqs = data.get("faqs", [])
        search_faqs.extend({**faq, "date": data["date"]} for faq in faqs)
        entries.append(
            {
                "date": data["date"],
                "period_start": data["period_start"],
                "period_end": data["period_end"],
                "faq_count": len(faqs),
                "summary": data["summary"],
                "generated_at": data["generated_at"],
            }
        )
    entries.sort(key=lambda item: item["date"], reverse=True)
    updated = entries[0]["generated_at"] if entries else None
    payload = {
        "version": 2,
        "updated_at": updated,
        "total_faqs": len(search_faqs),
        "search_path": "./data/search.json",
        "daily": entries,
    }
    search_payload = {
        "version": 1,
        "updated_at": updated,
        "total_faqs": len(search_faqs),
        "faqs": search_faqs,
    }
    INDEX.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    SEARCH.write_text(json.dumps(search_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {"daily_pages": len(entries), "total_faqs": len(search_faqs), "updated_at": updated},
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
