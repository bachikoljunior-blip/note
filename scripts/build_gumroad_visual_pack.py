#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
import struct
import sys
import zlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_booth_visual_pack import FONT  # noqa: E402

OUTPUT_DIR = ROOT / "dist" / "gumroad_visuals"
LAUNCHER = ROOT / "dist" / "gumroad_visual_pack.html"
REPORT = ROOT / "reports" / "gumroad_visual_pack.json"
TITLE_PATH = ROOT / "content" / "gumroad" / "title.txt"
DESCRIPTION_PATH = ROOT / "content" / "gumroad" / "description.md"

COVER_SIZE = (1280, 720)
THUMBNAIL_SIZE = (1200, 1200)
PRODUCT_MARKER = "NON-REPETITIVE AI TRIVIA SHORTS KIT"

ASSETS = [
    {
        "id": "cover_main",
        "filename": "gumroad_cover_main.png",
        "kind": "cover",
        "eyebrow": "ENGLISH CREATOR KIT",
        "headline": ["NON-REPETITIVE", "AI TRIVIA", "SHORTS KIT"],
        "metrics": ["100 TOPICS", "12 FORMATS", "30-DAY PLAN"],
        "footer": "RESEARCH  SCRIPT  VISUAL  ANALYZE",
        "purpose": "Main Gumroad product cover",
    },
    {
        "id": "cover_contents",
        "filename": "gumroad_cover_contents.png",
        "kind": "cover",
        "eyebrow": "WHAT YOU GET",
        "headline": ["BUILT TO TEST", "NOT JUST POST"],
        "metrics": ["PROMPT LIBRARY", "SOURCE LOG", "ANALYTICS"],
        "footer": "TOPICS  FORMATS  CALENDAR  WORKED EXAMPLE",
        "purpose": "Gumroad cover showing included resources",
    },
    {
        "id": "cover_workflow",
        "filename": "gumroad_cover_workflow.png",
        "kind": "cover",
        "eyebrow": "SMARTPHONE WORKFLOW",
        "headline": ["RESEARCH", "SCRIPT", "VISUAL", "ANALYZE"],
        "metrics": ["VERIFY SOURCES", "TEST 1 VARIABLE", "TRACK SALES"],
        "footer": "FROM IDEA TO 48H / 7D DECISION",
        "purpose": "Gumroad cover explaining the workflow",
    },
    {
        "id": "thumbnail",
        "filename": "gumroad_thumbnail.png",
        "kind": "thumbnail",
        "eyebrow": "100 TOPICS",
        "headline": ["AI TRIVIA", "SHORTS KIT"],
        "metrics": ["12 FORMATS", "30-DAY PLAN"],
        "footer": "ENGLISH  DIGITAL DOWNLOAD",
        "purpose": "Square Gumroad product thumbnail",
    },
]

Color = tuple[int, int, int]


def clamp(value: int) -> int:
    return max(0, min(255, value))


class Canvas:
    def __init__(self, width: int, height: int, variant: int) -> None:
        self.width = width
        self.height = height
        self.buf = bytearray(width * height * 3)
        palettes = [
            ((10, 18, 32), (19, 49, 57)),
            ((25, 15, 40), (57, 31, 43)),
            ((8, 26, 31), (18, 53, 48)),
            ((12, 19, 36), (31, 39, 72)),
        ]
        top, bottom = palettes[variant % len(palettes)]
        for y in range(height):
            t = y / max(1, height - 1)
            color = tuple(clamp(round(a + (b - a) * t)) for a, b in zip(top, bottom))
            start = y * width * 3
            self.buf[start:start + width * 3] = bytes(color) * width

    def set_pixel(self, x: int, y: int, color: Color) -> None:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        start = (y * self.width + x) * 3
        self.buf[start:start + 3] = bytes(color)

    def fill_rect(self, x: int, y: int, width: int, height: int, color: Color) -> None:
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.width, x + width), min(self.height, y + height)
        row = bytes(color) * max(0, x1 - x0)
        for yy in range(y0, y1):
            start = (yy * self.width + x0) * 3
            self.buf[start:start + len(row)] = row

    def rounded_rect(self, x: int, y: int, width: int, height: int, radius: int, color: Color) -> None:
        self.fill_rect(x + radius, y, width - radius * 2, height, color)
        self.fill_rect(x, y + radius, width, height - radius * 2, color)
        radius_squared = radius * radius
        for dy in range(radius):
            for dx in range(radius):
                if (dx - radius + 1) ** 2 + (dy - radius + 1) ** 2 <= radius_squared:
                    self.set_pixel(x + dx, y + dy, color)
                    self.set_pixel(x + width - 1 - dx, y + dy, color)
                    self.set_pixel(x + dx, y + height - 1 - dy, color)
                    self.set_pixel(x + width - 1 - dx, y + height - 1 - dy, color)

    @staticmethod
    def text_width(text: str, scale: int, spacing: int | None = None) -> int:
        spacing = scale if spacing is None else spacing
        if not text:
            return 0
        return len(text) * (5 * scale + spacing) - spacing

    def draw_text(
        self,
        text: str,
        x: int,
        y: int,
        scale: int,
        color: Color,
        spacing: int | None = None,
    ) -> int:
        spacing = scale if spacing is None else spacing
        cursor = x
        for char in text.upper():
            glyph = FONT.get(char, FONT[" "])
            for row_index, row in enumerate(glyph):
                for column_index, bit in enumerate(row):
                    if bit == "1":
                        self.fill_rect(
                            cursor + column_index * scale,
                            y + row_index * scale,
                            scale,
                            scale,
                            color,
                        )
            cursor += 5 * scale + spacing
        return cursor

    def centered_text(
        self,
        text: str,
        y: int,
        scale: int,
        color: Color,
        spacing: int | None = None,
    ) -> int:
        width = self.text_width(text, scale, spacing)
        self.draw_text(text, (self.width - width) // 2, y, scale, color, spacing)
        return width

    def fitting_scale(self, text: str, maximum: int, start: int, spacing: int = 4) -> int:
        scale = start
        while scale > 3 and self.text_width(text, scale, spacing) > maximum:
            scale -= 1
        return scale


def palette(variant: int) -> tuple[Color, Color, Color, Color]:
    accents = [(92, 255, 196), (255, 183, 78), (102, 218, 255), (165, 146, 255)]
    soft = [(31, 74, 70), (91, 51, 45), (30, 72, 77), (50, 48, 94)]
    return accents[variant], soft[variant], (245, 247, 250), (168, 180, 199)


def draw_decorations(canvas: Canvas, accent: Color, soft: Color) -> None:
    canvas.fill_rect(34, 34, 8, canvas.height - 68, accent)
    canvas.fill_rect(canvas.width - 42, 34, 8, canvas.height - 68, soft)
    for index in range(10):
        width = 22 + index * 7
        x = 70 + index * 113
        y = canvas.height - 22 - (index % 3) * 9
        canvas.fill_rect(x, y, width, 4, accent if index % 2 == 0 else soft)


def draw_cover(asset: dict[str, object], variant: int) -> tuple[Canvas, int]:
    width, height = COVER_SIZE
    canvas = Canvas(width, height, variant)
    accent, soft, white, muted = palette(variant)
    draw_decorations(canvas, accent, soft)

    canvas.rounded_rect(82, 38, width - 164, 64, 20, soft)
    eyebrow = str(asset["eyebrow"])
    eyebrow_scale = canvas.fitting_scale(eyebrow, 720, 7, 4)
    canvas.centered_text(eyebrow, 58, eyebrow_scale, accent, spacing=4)

    headline = list(asset["headline"])
    headline_max = 800
    if len(headline) == 2:
        y_positions = [170, 285]
        starts = [15, 14]
    elif len(headline) == 3:
        y_positions = [130, 230, 330]
        starts = [13, 14, 14]
    else:
        y_positions = [120, 205, 290, 375]
        starts = [10, 10, 10, 10]
    widest = 0
    for line, y, start in zip(headline, y_positions, starts):
        scale = canvas.fitting_scale(str(line), headline_max, start, 5)
        widest = max(widest, canvas.centered_text(str(line), y, scale, white, spacing=5))

    metrics = list(asset["metrics"])
    gap = 16
    total_width = 1080
    card_width = (total_width - gap * (len(metrics) - 1)) // len(metrics)
    card_x = (width - total_width) // 2
    card_y = 470
    for index, metric in enumerate(metrics):
        x = card_x + index * (card_width + gap)
        canvas.rounded_rect(x, card_y, card_width, 105, 20, soft)
        label = str(metric)
        scale = canvas.fitting_scale(label, card_width - 28, 7, 3)
        label_width = canvas.text_width(label, scale, 3)
        canvas.draw_text(label, x + (card_width - label_width) // 2, card_y + 38, scale, white, spacing=3)

    canvas.rounded_rect(82, 615, width - 164, 66, 20, (22, 28, 42))
    footer = str(asset["footer"])
    footer_scale = canvas.fitting_scale(footer, width - 220, 6, 4)
    canvas.centered_text(footer, 638, footer_scale, muted, spacing=4)
    return canvas, widest


def draw_thumbnail(asset: dict[str, object], variant: int) -> tuple[Canvas, int]:
    width, height = THUMBNAIL_SIZE
    canvas = Canvas(width, height, variant)
    accent, soft, white, muted = palette(variant)
    draw_decorations(canvas, accent, soft)

    canvas.rounded_rect(110, 105, width - 220, 110, 28, soft)
    eyebrow = str(asset["eyebrow"])
    scale = canvas.fitting_scale(eyebrow, 760, 11, 5)
    canvas.centered_text(eyebrow, 142, scale, accent, spacing=5)

    headline = list(asset["headline"])
    widest = 0
    for line, y in zip(headline, [350, 520]):
        scale = canvas.fitting_scale(str(line), 930, 20, 7)
        widest = max(widest, canvas.centered_text(str(line), y, scale, white, spacing=7))

    metrics = list(asset["metrics"])
    card_width = 440
    gap = 28
    start_x = (width - card_width * 2 - gap) // 2
    for index, metric in enumerate(metrics):
        x = start_x + index * (card_width + gap)
        canvas.rounded_rect(x, 760, card_width, 180, 28, soft)
        label = str(metric)
        scale = canvas.fitting_scale(label, card_width - 42, 10, 4)
        label_width = canvas.text_width(label, scale, 4)
        canvas.draw_text(label, x + (card_width - label_width) // 2, 825, scale, white, spacing=4)

    canvas.rounded_rect(110, 1020, width - 220, 100, 28, (22, 28, 42))
    footer = str(asset["footer"])
    footer_scale = canvas.fitting_scale(footer, width - 280, 8, 4)
    canvas.centered_text(footer, 1055, footer_scale, muted, spacing=4)
    return canvas, widest


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    checksum = zlib.crc32(kind + payload) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", checksum)


def encode_png(canvas: Canvas) -> bytes:
    raw = bytearray()
    stride = canvas.width * 3
    for y in range(canvas.height):
        raw.append(0)
        start = y * stride
        raw.extend(canvas.buf[start:start + stride])
    header = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", header)
        + png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + png_chunk(b"IEND", b"")
    )


def parse_png_dimensions(data: bytes) -> tuple[int, int]:
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or data[12:16] != b"IHDR":
        raise ValueError("invalid PNG signature")
    return struct.unpack(">II", data[16:24])


def build_launcher(results: list[dict[str, object]]) -> str:
    cards: list[str] = []
    for item in results:
        filename = html.escape(str(item["filename"]))
        purpose = html.escape(str(item["purpose"]))
        cards.append(f"""
        <article class="card">
          <img src="gumroad_visuals/{filename}" alt="{purpose}">
          <h2>{purpose}</h2>
          <p><code>{filename}</code><br>{item['width']}×{item['height']} / {item['bytes']:,} bytes</p>
          <a class="button" href="gumroad_visuals/{filename}" download>PNGを保存</a>
        </article>""")
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="color-scheme" content="light dark">
  <title>Gumroad英語商品画像パック</title>
  <style>
    :root {{ font-family: -apple-system,BlinkMacSystemFont,"Hiragino Sans","Yu Gothic",sans-serif; }}
    * {{ box-sizing: border-box; }} body {{ margin: 0; background: Canvas; color: CanvasText; }}
    main {{ max-width: 820px; margin: auto; padding: 20px 16px 36px; }}
    h1 {{ font-size: 1.5rem; line-height: 1.4; }} .lead {{ line-height: 1.7; opacity: .82; }}
    .grid {{ display: grid; gap: 18px; }} .card {{ border: 1px solid color-mix(in srgb,CanvasText 18%,transparent); border-radius: 18px; padding: 14px; }}
    img {{ width: 100%; height: auto; display: block; border-radius: 12px; }} h2 {{ font-size: 1.05rem; margin: 14px 0 8px; }}
    p {{ line-height: 1.55; }} code {{ overflow-wrap: anywhere; }} .button {{ display: block; width: 100%; padding: 14px; border-radius: 12px; text-align: center; text-decoration: none; font-weight: 750; background: CanvasText; color: Canvas; }}
  </style>
</head>
<body><main>
  <h1>Gumroad英語商品画像パック</h1>
  <p class="lead">横長カバー3枚と正方形サムネイル1枚です。英語商品と同じ事実だけを使い、外部素材・外部フォント・有料サービスなしで再生成できます。重要なタイトルは横長画像の中央安全領域に収めています。iPhoneで保存ボタンが画像表示になる場合は、共有メニューから「ファイルに保存」を選んでください。</p>
  <p><a class="button" href="gumroad_listing_launcher.html">出品文・価格・ZIPのランチャーへ戻る</a></p>
  <section class="grid">{''.join(cards)}</section>
</main></body></html>
"""


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    results: list[dict[str, object]] = []

    title = TITLE_PATH.read_text(encoding="utf-8").strip()
    description = DESCRIPTION_PATH.read_text(encoding="utf-8").strip()
    if PRODUCT_MARKER not in title.upper():
        errors.append("product_title_marker_missing")
    for marker in ("100", "12", "30-day", "prompt", "source", "analytics"):
        if marker.lower() not in description.lower():
            errors.append(f"product_description_fact_missing:{marker}")

    if len(ASSETS) != 4:
        errors.append("asset_count_must_be_4")

    for index, asset in enumerate(ASSETS):
        rendered_strings = [
            str(asset["eyebrow"]),
            *[str(item) for item in asset["headline"]],
            *[str(item) for item in asset["metrics"]],
            str(asset["footer"]),
        ]
        unsupported = sorted({
            char
            for value in rendered_strings
            for char in value.upper()
            if char not in FONT
        })
        if unsupported:
            errors.append(f"unsupported_glyphs:{asset['id']}:{''.join(unsupported)}")
        kind = str(asset["kind"])
        canvas, title_width = (
            draw_thumbnail(asset, index) if kind == "thumbnail" else draw_cover(asset, index)
        )
        data = encode_png(canvas)
        width, height = parse_png_dimensions(data)
        expected = THUMBNAIL_SIZE if kind == "thumbnail" else COVER_SIZE
        filename = str(asset["filename"])
        output = OUTPUT_DIR / filename
        output.write_bytes(data)

        if not filename.endswith(".png"):
            errors.append(f"not_png:{filename}")
        if (width, height) != expected:
            errors.append(f"wrong_dimensions:{filename}:{width}x{height}")
        if len(data) < 8_000:
            errors.append(f"suspiciously_small:{filename}:{len(data)}")
        if kind == "cover" and title_width > 820:
            errors.append(f"cover_title_outside_center_safe_zone:{filename}:{title_width}")

        results.append({
            "id": asset["id"],
            "kind": kind,
            "filename": filename,
            "path": str(output.relative_to(ROOT)),
            "purpose": asset["purpose"],
            "width": width,
            "height": height,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "centered_title_width": title_width,
        })

    launcher = build_launcher(results)
    LAUNCHER.parent.mkdir(parents=True, exist_ok=True)
    LAUNCHER.write_text(launcher, encoding="utf-8")
    if "TODO" in launcher or "[confirm]" in launcher.lower():
        errors.append("placeholder_found")

    payload = {
        "ok": not errors,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "channel": "Gumroad",
        "language": "English",
        "purpose": "cover and thumbnail assets for product understanding and conversion",
        "asset_count": len(results),
        "cover_dimensions": list(COVER_SIZE),
        "thumbnail_dimensions": list(THUMBNAIL_SIZE),
        "format": "PNG",
        "external_assets": 0,
        "external_fonts": 0,
        "cost_yen": 0,
        "launcher": str(LAUNCHER.relative_to(ROOT)),
        "launcher_sha256": hashlib.sha256(launcher.encode("utf-8")).hexdigest(),
        "assets": results,
        "errors": errors,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
