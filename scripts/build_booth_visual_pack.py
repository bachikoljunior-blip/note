#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
import struct
import zlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "dist" / "booth_visuals"
LAUNCHER = ROOT / "dist" / "booth_visual_pack.html"
REPORT = ROOT / "reports" / "booth_visual_pack.json"

WIDTH = 1200
HEIGHT = 1200
PRODUCT_TITLE = "AI SHORTS CREATOR KIT"
ASSETS = [
    {
        "id": "main",
        "filename": "booth_cover_main.png",
        "eyebrow": "MOBILE READY",
        "headline": ["AI SHORTS", "CREATOR KIT"],
        "metrics": ["100 TOPICS", "12 FORMATS", "30 DAY PLAN"],
        "footer": "RESEARCH  SCRIPT  VISUAL  ANALYZE",
        "purpose": "BOOTHの主商品画像",
    },
    {
        "id": "contents",
        "filename": "booth_cover_contents.png",
        "eyebrow": "WHAT'S INSIDE",
        "headline": ["BUILD FAST", "WITHOUT LOOKING", "MASS-PRODUCED"],
        "metrics": ["PROMPT LIBRARY", "SOURCE LOG", "ANALYTICS"],
        "footer": "TOPICS  FORMATS  CALENDAR  WORKED EXAMPLE",
        "purpose": "収録内容を伝える補助画像",
    },
    {
        "id": "workflow",
        "filename": "booth_cover_workflow.png",
        "eyebrow": "SMARTPHONE WORKFLOW",
        "headline": ["RESEARCH", "SCRIPT", "VISUAL", "ANALYZE"],
        "metrics": ["VERIFY SOURCES", "CHANGE 1 VARIABLE", "TRACK SALES"],
        "footer": "FROM IDEA TO 48H / 7D DECISION",
        "purpose": "スマホ対応と運用手順を伝える補助画像",
    },
]

FONT: dict[str, tuple[str, ...]] = {
    " ": ("00000",) * 7,
    "A": ("01110","10001","10001","11111","10001","10001","10001"),
    "B": ("11110","10001","10001","11110","10001","10001","11110"),
    "C": ("01111","10000","10000","10000","10000","10000","01111"),
    "D": ("11110","10001","10001","10001","10001","10001","11110"),
    "E": ("11111","10000","10000","11110","10000","10000","11111"),
    "F": ("11111","10000","10000","11110","10000","10000","10000"),
    "G": ("01111","10000","10000","10111","10001","10001","01111"),
    "H": ("10001","10001","10001","11111","10001","10001","10001"),
    "I": ("11111","00100","00100","00100","00100","00100","11111"),
    "J": ("00111","00010","00010","00010","10010","10010","01100"),
    "K": ("10001","10010","10100","11000","10100","10010","10001"),
    "L": ("10000","10000","10000","10000","10000","10000","11111"),
    "M": ("10001","11011","10101","10101","10001","10001","10001"),
    "N": ("10001","11001","10101","10011","10001","10001","10001"),
    "O": ("01110","10001","10001","10001","10001","10001","01110"),
    "P": ("11110","10001","10001","11110","10000","10000","10000"),
    "Q": ("01110","10001","10001","10001","10101","10010","01101"),
    "R": ("11110","10001","10001","11110","10100","10010","10001"),
    "S": ("01111","10000","10000","01110","00001","00001","11110"),
    "T": ("11111","00100","00100","00100","00100","00100","00100"),
    "U": ("10001","10001","10001","10001","10001","10001","01110"),
    "V": ("10001","10001","10001","10001","10001","01010","00100"),
    "W": ("10001","10001","10001","10101","10101","10101","01010"),
    "X": ("10001","10001","01010","00100","01010","10001","10001"),
    "Y": ("10001","10001","01010","00100","00100","00100","00100"),
    "Z": ("11111","00001","00010","00100","01000","10000","11111"),
    "0": ("01110","10001","10011","10101","11001","10001","01110"),
    "1": ("00100","01100","00100","00100","00100","00100","01110"),
    "2": ("01110","10001","00001","00010","00100","01000","11111"),
    "3": ("11110","00001","00001","01110","00001","00001","11110"),
    "4": ("00010","00110","01010","10010","11111","00010","00010"),
    "5": ("11111","10000","10000","11110","00001","00001","11110"),
    "6": ("01110","10000","10000","11110","10001","10001","01110"),
    "7": ("11111","00001","00010","00100","01000","01000","01000"),
    "8": ("01110","10001","10001","01110","10001","10001","01110"),
    "9": ("01110","10001","10001","01111","00001","00001","01110"),
    "-": ("00000","00000","00000","11111","00000","00000","00000"),
    "/": ("00001","00010","00010","00100","01000","01000","10000"),
    ":": ("00000","00100","00100","00000","00100","00100","00000"),
    "'": ("00100","00100","00000","00000","00000","00000","00000"),
    ".": ("00000","00000","00000","00000","00000","00110","00110"),
}

Color = tuple[int, int, int]


def clamp(v: int) -> int:
    return max(0, min(255, v))


def set_pixel(buf: bytearray, x: int, y: int, color: Color) -> None:
    if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
        return
    i = (y * WIDTH + x) * 3
    buf[i:i+3] = bytes(color)


def fill_rect(buf: bytearray, x: int, y: int, w: int, h: int, color: Color) -> None:
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(WIDTH, x + w), min(HEIGHT, y + h)
    row = bytes(color) * max(0, x1 - x0)
    for yy in range(y0, y1):
        i = (yy * WIDTH + x0) * 3
        buf[i:i+len(row)] = row


def fill_rounded_rect(buf: bytearray, x: int, y: int, w: int, h: int, r: int, color: Color) -> None:
    fill_rect(buf, x + r, y, w - 2 * r, h, color)
    fill_rect(buf, x, y + r, w, h - 2 * r, color)
    rr = r * r
    for dy in range(r):
        for dx in range(r):
            if (dx - r + 1) ** 2 + (dy - r + 1) ** 2 <= rr:
                set_pixel(buf, x + dx, y + dy, color)
                set_pixel(buf, x + w - 1 - dx, y + dy, color)
                set_pixel(buf, x + dx, y + h - 1 - dy, color)
                set_pixel(buf, x + w - 1 - dx, y + h - 1 - dy, color)


def draw_text(buf: bytearray, text: str, x: int, y: int, scale: int, color: Color, spacing: int | None = None) -> int:
    text = text.upper()
    spacing = scale if spacing is None else spacing
    cursor = x
    for char in text:
        glyph = FONT.get(char, FONT[" "])
        for row_i, row in enumerate(glyph):
            for col_i, bit in enumerate(row):
                if bit == "1":
                    fill_rect(buf, cursor + col_i * scale, y + row_i * scale, scale, scale, color)
        cursor += 5 * scale + spacing
    return cursor


def text_width(text: str, scale: int, spacing: int | None = None) -> int:
    spacing = scale if spacing is None else spacing
    if not text:
        return 0
    return len(text) * (5 * scale + spacing) - spacing


def centered_text(buf: bytearray, text: str, y: int, scale: int, color: Color, spacing: int | None = None) -> None:
    draw_text(buf, text, (WIDTH - text_width(text, scale, spacing)) // 2, y, scale, color, spacing)


def make_canvas(variant: int) -> bytearray:
    buf = bytearray(WIDTH * HEIGHT * 3)
    for y in range(HEIGHT):
        t = y / max(1, HEIGHT - 1)
        if variant == 0:
            base = (15 + int(15 * t), 18 + int(12 * t), 28 + int(18 * t))
        elif variant == 1:
            base = (20 + int(8 * t), 16 + int(12 * t), 32 + int(20 * t))
        else:
            base = (11 + int(10 * t), 27 + int(12 * t), 29 + int(10 * t))
        row = bytes(tuple(clamp(c) for c in base)) * WIDTH
        i = y * WIDTH * 3
        buf[i:i+len(row)] = row
    return buf


def draw_asset(asset: dict[str, object], variant: int) -> bytearray:
    buf = make_canvas(variant)
    accent: Color = [(92, 255, 196), (255, 186, 73), (108, 214, 255)][variant]
    soft: Color = [(39, 83, 73), (87, 57, 38), (35, 75, 82)][variant]
    white: Color = (245, 247, 250)
    muted: Color = (170, 180, 194)

    fill_rect(buf, 58, 58, 12, HEIGHT - 116, accent)
    fill_rect(buf, WIDTH - 70, 58, 12, HEIGHT - 116, soft)
    fill_rounded_rect(buf, 102, 92, 996, 96, 28, soft)
    centered_text(buf, str(asset["eyebrow"]), 121, 8, accent, spacing=5)

    headline = list(asset["headline"])
    if len(headline) == 2:
        sizes = [22, 18]
        ys = [280, 470]
    elif len(headline) == 3:
        sizes = [15, 13, 13]
        ys = [270, 405, 540]
    else:
        sizes = [16, 16, 16, 16]
        ys = [250, 365, 480, 595]
    for line, scale, yy in zip(headline, sizes, ys):
        centered_text(buf, str(line), yy, scale, white, spacing=max(5, scale // 2))

    metrics = list(asset["metrics"])
    box_y = 730 if len(headline) <= 3 else 735
    gap = 20
    box_w = (996 - gap * (len(metrics) - 1)) // len(metrics)
    for idx, metric in enumerate(metrics):
        bx = 102 + idx * (box_w + gap)
        fill_rounded_rect(buf, bx, box_y, box_w, 170, 24, soft)
        words = str(metric).split()
        if len(words) == 1:
            line1, line2 = words[0], ""
        elif len(words) == 2:
            combined = " ".join(words)
            if text_width(combined, 6, 4) <= box_w - 34:
                line1, line2 = combined, ""
            else:
                line1, line2 = words
        else:
            split = (len(words) + 1) // 2
            line1 = " ".join(words[:split])
            line2 = " ".join(words[split:])

        def fitting_scale(value: str, maximum: int, start: int) -> int:
            scale = start
            while scale > 3 and text_width(value, scale, 3) > maximum:
                scale -= 1
            return scale

        if line2:
            scale = fitting_scale(line1, box_w - 34, 7)
            scale2 = fitting_scale(line2, box_w - 34, 7)
            draw_text(buf, line1, bx + (box_w - text_width(line1, scale, 3)) // 2, box_y + 38, scale, white, spacing=3)
            draw_text(buf, line2, bx + (box_w - text_width(line2, scale2, 3)) // 2, box_y + 101, scale2, accent, spacing=3)
        else:
            scale = fitting_scale(line1, box_w - 34, 8)
            draw_text(buf, line1, bx + (box_w - text_width(line1, scale, 3)) // 2, box_y + 73, scale, white, spacing=3)

    fill_rounded_rect(buf, 102, 970, 996, 118, 28, (25, 30, 42))
    footer = str(asset["footer"])
    footer_scale = 6 if text_width(footer, 6, 4) <= 920 else 5
    centered_text(buf, footer, 1009, footer_scale, muted, spacing=4)
    return buf


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def encode_png(buf: bytearray) -> bytes:
    raw = bytearray()
    stride = WIDTH * 3
    for y in range(HEIGHT):
        raw.append(0)
        start = y * stride
        raw.extend(buf[start:start+stride])
    header = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", header) + png_chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + png_chunk(b"IEND", b"")


def parse_png_dimensions(data: bytes) -> tuple[int, int]:
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or data[12:16] != b"IHDR":
        raise ValueError("invalid PNG signature")
    return struct.unpack(">II", data[16:24])


def build_launcher(results: list[dict[str, object]]) -> str:
    cards = []
    for item in results:
        filename = html.escape(str(item["filename"]))
        purpose = html.escape(str(item["purpose"]))
        cards.append(f"""
        <article class="card">
          <img src="booth_visuals/{filename}" alt="{purpose}">
          <h2>{purpose}</h2>
          <p><code>{filename}</code> / {item['bytes']:,} bytes</p>
          <a class="button" href="booth_visuals/{filename}" download>PNGを保存</a>
        </article>""")
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="color-scheme" content="light dark">
  <title>BOOTH商品画像パック</title>
  <style>
    :root {{ font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Yu Gothic", sans-serif; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: Canvas; color: CanvasText; }}
    main {{ max-width: 780px; margin: 0 auto; padding: 20px 16px 32px; }}
    h1 {{ font-size: 1.5rem; line-height: 1.4; }}
    .lead {{ line-height: 1.7; opacity: .8; }}
    .grid {{ display: grid; gap: 18px; }}
    .card {{ border: 1px solid color-mix(in srgb, CanvasText 18%, transparent); border-radius: 18px; padding: 14px; }}
    img {{ width: 100%; height: auto; display: block; border-radius: 12px; }}
    h2 {{ font-size: 1.05rem; margin: 14px 0 8px; }}
    p {{ line-height: 1.5; }}
    code {{ overflow-wrap: anywhere; }}
    .button {{ display: block; width: 100%; padding: 14px; border-radius: 12px; text-align: center; text-decoration: none; font-weight: 750; background: CanvasText; color: Canvas; }}
  </style>
</head>
<body>
<main>
  <h1>BOOTH商品画像パック</h1>
  <p class="lead">主画像1枚と、内容・スマホ運用を説明する補助画像2枚です。すべて1200×1200 PNG、外部素材・外部フォント・有料サービス不使用です。BOOTHの商品画像欄で3枚まとめて選択できます。</p>
  <section class="grid">{''.join(cards)}</section>
</main>
</body>
</html>
"""


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    results: list[dict[str, object]] = []

    if len(ASSETS) != 3:
        errors.append("asset_count_must_be_3")

    for idx, asset in enumerate(ASSETS):
        filename = str(asset["filename"])
        if not filename.endswith(".png"):
            errors.append(f"not_png:{filename}")
            continue
        data = encode_png(draw_asset(asset, idx))
        width, height = parse_png_dimensions(data)
        output = OUTPUT_DIR / filename
        output.write_bytes(data)
        if (width, height) != (WIDTH, HEIGHT):
            errors.append(f"wrong_dimensions:{filename}:{width}x{height}")
        if len(data) < 10_000:
            errors.append(f"suspiciously_small:{filename}:{len(data)}")
        results.append({
            "id": asset["id"],
            "filename": filename,
            "path": str(output.relative_to(ROOT)),
            "purpose": asset["purpose"],
            "width": width,
            "height": height,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })

    launcher = build_launcher(results)
    LAUNCHER.parent.mkdir(parents=True, exist_ok=True)
    LAUNCHER.write_text(launcher, encoding="utf-8")
    if PRODUCT_TITLE not in Path(__file__).read_text(encoding="utf-8"):
        errors.append("product_title_marker_missing")
    if "TODO" in launcher or "[要確認]" in launcher:
        errors.append("placeholder_found")

    payload = {
        "ok": not errors,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "channel": "BOOTH",
        "purpose": "商品画像による理解・信頼・購入転換の改善",
        "asset_count": len(results),
        "dimensions": [WIDTH, HEIGHT],
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
