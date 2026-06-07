#!/usr/bin/env python3
"""
Convert a PNG into a layered SVG.

The output SVG contains one <g> per detected color layer. Each group embeds a
transparent PNG mask for that layer, which keeps the result easy to inspect and
edit in tools that understand SVG layer/group structure.

This is not a full vector tracer. It creates a multi-layer SVG container from a
raster input with a pragmatic, dependency-light pipeline.
"""

from __future__ import annotations

import argparse
import base64
import io
import re
from collections import Counter
from pathlib import Path
from typing import Iterable

from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read a PNG and create a layered SVG file."
    )
    parser.add_argument("input_png", type=Path, help="Path to the source PNG file.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Path to the output SVG file. Defaults to <input-stem>_layered.svg.",
    )
    parser.add_argument(
        "--colors",
        type=int,
        default=8,
        help="Maximum number of color layers to keep after quantization.",
    )
    parser.add_argument(
        "--min-pixels",
        type=int,
        default=24,
        help="Drop tiny layers below this pixel count.",
    )
    parser.add_argument(
        "--alpha-threshold",
        type=int,
        default=8,
        help="Pixels with alpha below this are treated as transparent.",
    )
    return parser.parse_args()


def sanitize_id(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", value).strip("_") or "layer"


def encode_png_base64(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def rgba_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def quantize_image(
    image: Image.Image, max_colors: int, alpha_threshold: int
) -> tuple[Image.Image, list[tuple[int, int, int]], list[int]]:
    rgba = image.convert("RGBA")
    white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    opaque = Image.alpha_composite(white_bg, rgba)
    quantized = opaque.convert("RGB").quantize(colors=max_colors, method=Image.MEDIANCUT)

    palette = quantized.getpalette()[: max_colors * 3]
    colors: list[tuple[int, int, int]] = []
    for index in range(len(palette) // 3):
        offset = index * 3
        colors.append((palette[offset], palette[offset + 1], palette[offset + 2]))

    alpha = rgba.getchannel("A")
    indices = list(quantized.get_flattened_data())
    alpha_values = list(alpha.get_flattened_data())
    for pos, alpha_value in enumerate(alpha_values):
        if alpha_value < alpha_threshold:
            indices[pos] = -1

    return rgba, colors, indices


def build_layer_images(
    rgba: Image.Image,
    colors: list[tuple[int, int, int]],
    indices: list[int],
    min_pixels: int,
) -> list[dict[str, object]]:
    width, height = rgba.size
    counts = Counter(index for index in indices if index >= 0)
    raw_pixels = list(rgba.get_flattened_data())
    layers: list[dict[str, object]] = []

    for color_index, pixel_count in counts.most_common():
        if pixel_count < min_pixels or color_index >= len(colors):
            continue

        layer_pixels = []
        for pos, pixel in enumerate(raw_pixels):
            if indices[pos] == color_index:
                layer_pixels.append(pixel)
            else:
                layer_pixels.append((0, 0, 0, 0))

        layer_image = Image.new("RGBA", (width, height))
        layer_image.putdata(layer_pixels)
        rgb = colors[color_index]
        layers.append(
            {
                "id": sanitize_id(
                    f"layer_{len(layers) + 1}_{rgba_to_hex(rgb)[1:].lower()}_{pixel_count}px"
                ),
                "label": f"Layer {len(layers) + 1} {rgba_to_hex(rgb)}",
                "pixel_count": pixel_count,
                "color": rgba_to_hex(rgb),
                "image": layer_image,
            }
        )

    return layers


def build_svg(
    width: int,
    height: int,
    source_name: str,
    layers: Iterable[dict[str, object]],
) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
            f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        ),
        f"  <title>{source_name} layered export</title>",
        "  <desc>Generated from a PNG by splitting the image into color-based raster layers.</desc>",
    ]

    for layer in layers:
        encoded = encode_png_base64(layer["image"])  # type: ignore[arg-type]
        layer_id = layer["id"]
        label = layer["label"]
        pixel_count = layer["pixel_count"]
        color = layer["color"]
        lines.extend(
            [
                (
                    f'  <g id="{layer_id}" inkscape:groupmode="layer" '
                    f'inkscape:label="{label}" data-color="{color}" '
                    f'data-pixels="{pixel_count}">'
                ),
                (
                    f'    <image x="0" y="0" width="{width}" height="{height}" '
                    f'xlink:href="data:image/png;base64,{encoded}" />'
                ),
                "  </g>",
            ]
        )

    lines.append("</svg>")
    return "\n".join(lines)


def ensure_svg_output_path(input_path: Path, output_path: Path | None) -> Path:
    if output_path is not None:
        return output_path
    return input_path.with_name(f"{input_path.stem}_layered.svg")


def main() -> int:
    args = parse_args()
    input_path = args.input_png
    output_path = ensure_svg_output_path(input_path, args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")
    if input_path.suffix.lower() != ".png":
        raise ValueError("Input must be a PNG file.")
    if args.colors < 1:
        raise ValueError("--colors must be at least 1.")
    if args.min_pixels < 1:
        raise ValueError("--min-pixels must be at least 1.")
    if not 0 <= args.alpha_threshold <= 255:
        raise ValueError("--alpha-threshold must be between 0 and 255.")

    with Image.open(input_path) as source_image:
        rgba, colors, indices = quantize_image(
            source_image, max_colors=args.colors, alpha_threshold=args.alpha_threshold
        )
        layers = build_layer_images(
            rgba=rgba, colors=colors, indices=indices, min_pixels=args.min_pixels
        )

    if not layers:
        raise RuntimeError(
            "No layers were produced. Try lowering --min-pixels or increasing --colors."
        )

    svg = build_svg(
        width=rgba.width,
        height=rgba.height,
        source_name=input_path.name,
        layers=layers,
    )
    output_path.write_text(svg, encoding="utf-8")

    print(f"Wrote {output_path} with {len(layers)} layer(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
