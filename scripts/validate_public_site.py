#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAILY = ROOT / "data" / "daily"

ALLOWED_URL_PREFIXES = (
    "http://localhost:4173",
    "https://techkwon.github.io/brickbot-faq",
    "https://docs.google.com/spreadsheets/d/1vdCn7XlzJpcHMTnOJdjOl3x7PR_AkNZhH-VQxN7CCm0/",
    "https://ai-goe.spoonk7.workers.dev/view/m",
    "https://ai-goe.spoonk7.workers.dev/hub/materials",
    "https://open.kakao.com/o/sfXx4RZg",
    "https://drive.google.com/drive/folders/1TDFUgqfaqShVC6fs3c4qTfaMUMV-z2MF",
    "https://drive.google.com/drive/folders/1oAoQKTHVwMGr5vwGa323y1vlv5KhS5ab",
    "https://drive.google.com/drive/folders/1_Sj1P2iL5r0jHXJaNBWSeecEVTplI49B",
    "https://discord.gg/uHFejFphC",
    "https://padlet.com/Lecoeur_dr/2026-2-zpl0jnrtnfsqtz4z",
    "https://kocoafab.cc/edu/kocomate",
)
TEXT_SUFFIXES = {".html", ".css", ".js", ".json", ".md", ".txt", ".yml", ".yaml"}
FORBIDDEN_DOMAINS: set[str] = set()
FORBIDDEN_FRAGMENTS = {
    "/Users/techkwon",
    "KAKAOCLI_USER_ID",
    "kakaocli-user-id",
    "brickbot-group-messages.sqlite3",
    "chat_id",
    "message_id",
    "sender_id",
    "sender_name",
    "raw_json",
}
DAILY_KEYS = {"date", "period_start", "period_end", "generated_at", "summary", "stats", "faqs"}
FAQ_KEYS = {"id", "question", "answer", "category", "tags", "status", "source_count"}
STAT_KEYS = {"messages_reviewed", "questions_detected", "changes", "excluded"}
CATEGORIES = {"공통", "원격", "집합", "교과", "강사배치", "자료", "기타"}
STATUSES = {"확인됨", "검수 필요", "변경됨"}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_daily(path: Path, errors: list[str]) -> None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(errors, f"{path.relative_to(ROOT)}: invalid JSON ({type(exc).__name__})")
        return
    extra = set(data) - DAILY_KEYS
    missing = DAILY_KEYS - set(data)
    if extra or missing:
        fail(errors, f"{path.relative_to(ROOT)}: daily keys extra={sorted(extra)} missing={sorted(missing)}")
    if path.stem != data.get("date"):
        fail(errors, f"{path.relative_to(ROOT)}: filename/date mismatch")
    if not isinstance(data.get("summary"), str) or not data.get("summary", "").strip():
        fail(errors, f"{path.relative_to(ROOT)}: summary required")
    stats = data.get("stats")
    if not isinstance(stats, dict) or set(stats) != STAT_KEYS or any(not isinstance(v, int) or v < 0 for v in stats.values()):
        fail(errors, f"{path.relative_to(ROOT)}: invalid stats")
    faqs = data.get("faqs")
    if not isinstance(faqs, list) or len(faqs) > 30:
        fail(errors, f"{path.relative_to(ROOT)}: faqs must be list with <=30 items")
        return
    seen = set()
    for index, faq in enumerate(faqs):
        label = f"{path.relative_to(ROOT)} faq[{index}]"
        if not isinstance(faq, dict) or set(faq) != FAQ_KEYS:
            fail(errors, f"{label}: invalid keys")
            continue
        if faq["id"] in seen:
            fail(errors, f"{label}: duplicate id")
        seen.add(faq["id"])
        if faq["category"] not in CATEGORIES:
            fail(errors, f"{label}: invalid category")
        if faq["status"] not in STATUSES:
            fail(errors, f"{label}: invalid status")
        if not isinstance(faq["source_count"], int) or faq["source_count"] < 1:
            fail(errors, f"{label}: source_count must be positive")
        if not isinstance(faq["tags"], list) or len(faq["tags"]) > 8 or any(not isinstance(x, str) for x in faq["tags"]):
            fail(errors, f"{label}: invalid tags")
        for key in ("id", "question", "answer"):
            if not isinstance(faq[key], str) or not faq[key].strip():
                fail(errors, f"{label}: {key} required")
        if len(str(faq["question"])) > 180 or len(str(faq["answer"])) > 1200:
            fail(errors, f"{label}: content too long")


def scan_text(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    rel = path.relative_to(ROOT)
    for fragment in FORBIDDEN_FRAGMENTS:
        if fragment in text:
            fail(errors, f"{rel}: forbidden fragment {fragment!r}")
    for domain in FORBIDDEN_DOMAINS:
        if domain in text:
            fail(errors, f"{rel}: internal domain found")
    for url in re.findall(r"https?://[^\s\"'<>`)]+", text):
        if not url.startswith(ALLOWED_URL_PREFIXES):
            fail(errors, f"{rel}: external URL is not allowed")
    if re.search(r"\b01[016789]-?\d{3,4}-?\d{4}\b", text):
        fail(errors, f"{rel}: possible phone number")
    if re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.IGNORECASE):
        fail(errors, f"{rel}: possible email address")
    if re.search(r"(?<![A-Fa-f0-9])\d{15,20}(?![A-Fa-f0-9])", text):
        fail(errors, f"{rel}: possible internal numeric identifier")
    if re.search(r"(?:비밀번호|비번|password|secret)\s*[:=]\s*\S+", text, re.IGNORECASE):
        fail(errors, f"{rel}: possible credential")
    if re.search(r"\btoken\s*[:=]\s*[A-Za-z0-9_./+-]{16,}", text, re.IGNORECASE):
        fail(errors, f"{rel}: possible token")


def main() -> int:
    errors: list[str] = []
    validator = Path(__file__).resolve()
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.resolve() == validator or ".git" in path.parts or "_site" in path.parts:
            continue
        if path.suffix in {".sqlite", ".sqlite3", ".db", ".jsonl", ".log"}:
            fail(errors, f"{path.relative_to(ROOT)}: private file type")
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {".gitignore", ".nojekyll"}:
            scan_text(path, errors)
    for path in DAILY.glob("*.json"):
        validate_daily(path, errors)
    if errors:
        print("PUBLIC SITE VALIDATION FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "ok", "daily_pages": len(list(DAILY.glob('*.json')))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
