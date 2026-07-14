#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAILY = ROOT / "data" / "daily"
INDEX = ROOT / "data" / "index.json"


def main() -> int:
    DAILY.mkdir(parents=True, exist_ok=True)
    entries = []
    for path in sorted(DAILY.glob("*.json"), reverse=True):
        data = json.loads(path.read_text(encoding="utf-8"))
        faqs = data.get("faqs", [])
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
    payload = {"version": 1, "updated_at": updated, "daily": entries}
    INDEX.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"daily_pages": len(entries), "updated_at": updated}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
