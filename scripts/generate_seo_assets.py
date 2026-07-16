#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size=size)


def draw_logo(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], letter_size: int) -> None:
    draw.rounded_rectangle(box, radius=24, fill="#FFD84D", outline="#111827", width=5)
    x1, y1, x2, y2 = box
    label = "B"
    fnt = font(letter_size)
    bounds = draw.textbbox((0, 0), label, font=fnt)
    x = x1 + ((x2 - x1) - (bounds[2] - bounds[0])) // 2
    y = y1 + ((y2 - y1) - (bounds[3] - bounds[1])) // 2 - bounds[1]
    draw.text((x, y), label, font=fnt, fill="#111827")


def build_og() -> None:
    image = Image.new("RGB", (1200, 630), "#FFFDF5")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1200, 26), fill="#FFD84D")
    draw_logo(draw, (72, 66, 210, 204), 92)
    draw.text((244, 76), "BRICKBOT FAQ", font=font(54), fill="#111827")
    draw.text((244, 145), "2026 · 2권역 · 중등 강사진", font=font(26), fill="#4B5563")
    draw.text((72, 274), "찾는 답을", font=font(78), fill="#111827")
    draw.text((72, 366), "빠르게.", font=font(92), fill="#2252D1")
    draw.rounded_rectangle((710, 276, 1128, 496), radius=28, fill="#FFD84D", outline="#111827", width=5)
    draw.text((758, 316), "원격 · 집합", font=font(43), fill="#111827")
    draw.text((758, 380), "교과 · 강사배치", font=font(43), fill="#111827")
    draw.text((72, 552), "개인정보를 제외한 확인된 공개 FAQ", font=font(28), fill="#4B5563")
    image.save(ASSETS / "og-brickbot-faq.png", optimize=True)


def build_touch_icon() -> None:
    image = Image.new("RGB", (180, 180), "#FFFDF5")
    draw = ImageDraw.Draw(image)
    draw_logo(draw, (14, 14, 166, 166), 104)
    image.save(ASSETS / "apple-touch-icon.png", optimize=True)


if __name__ == "__main__":
    ASSETS.mkdir(parents=True, exist_ok=True)
    build_og()
    build_touch_icon()
    print(ASSETS / "og-brickbot-faq.png")
    print(ASSETS / "apple-touch-icon.png")
