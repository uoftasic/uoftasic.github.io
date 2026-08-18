#!/usr/bin/env python3
"""Re-colour a Tiny Tapeout GDS render into the U of T palette.

Tiny Tapeout publishes a permanent render of every shuttle project at
github.com/TinyTapeout/tinytapeout-project-renders. Those renders use KLayout's
default layer colours — saturated magenta, cyan and pure blue — which fight the
site palette. Layer colours are only a display convention, so remapping them
changes nothing about the geometry: every trace is still exactly where it was
routed.

Usage
-----
    # fetch straight from Tiny Tapeout's render mirror
    python3 script/reink-render.py --shuttle ttsky25b \\
        --module tt_um_ieeeuoftasic_simproc --slug simproc

    # or re-ink a local file
    python3 script/reink-render.py --input render.png --slug simproc

Writes assets/projects/<slug>-die.png (project card and spec rail),
<slug>-hero.png (magnified crop for the home hero) and <slug>-og.png (social
preview).

Requires Pillow:  pip install pillow
"""

from __future__ import annotations

import argparse
import io
import sys
import urllib.request
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required:  pip install pillow")

HERO_UPSCALE = 3  # 1200px crop -> 3600px asset, wider than any common display

RENDER_URL = (
    "https://raw.githubusercontent.com/TinyTapeout/tinytapeout-project-renders"
    "/main/shuttles/{shuttle}/{module}/render.png"
)

# U of T palette
BLUE, TEAL, LIGHT_BLUE = (30, 55, 101), (0, 127, 163), (93, 140, 190)
PALE, CREAM, INK, YELLOW = (214, 224, 232), (238, 233, 222), (18, 26, 44), (241, 197, 0)

# KLayout's default SKY130 layer colours -> ours. Blue dominates so the result
# reads as U of T Blue; vias stay yellow because they are the sparse accent that
# gives the image its life.
PALETTE = {
    (0, 0, 255): BLUE,            # met1
    (255, 0, 255): LIGHT_BLUE,    # met2
    (0, 255, 255): TEAL,          # met3
    (255, 230, 191): CREAM,       # fill
    (94, 0, 230): INK,            # via
    (255, 255, 255): (252, 251, 248),
    (191, 64, 38): YELLOW,
    (0, 255, 0): PALE,
    (204, 204, 217): (232, 230, 222),
    (255, 128, 0): YELLOW,
    (255, 0, 0): YELLOW,
    (38, 140, 107): TEAL,
    (230, 31, 13): YELLOW,
    (255, 255, 204): (245, 242, 232),
    (0, 204, 102): PALE,
    (153, 0, 230): INK,
    (255, 255, 0): YELLOW,
}


def reink(src: Image.Image) -> Image.Image:
    """Map every pixel to the nearest palette entry, memoised per colour."""
    src = src.convert("RGB")
    out = Image.new("RGB", src.size)
    src_px, out_px = src.load(), out.load()
    cache: dict[tuple, tuple] = {}
    width, height = src.size
    for y in range(height):
        for x in range(width):
            colour = src_px[x, y]
            mapped = cache.get(colour)
            if mapped is None:
                mapped = PALETTE.get(colour)
                if mapped is None:
                    mapped = min(
                        PALETTE.items(),
                        key=lambda kv: sum((a - b) ** 2 for a, b in zip(kv[0], colour)),
                    )[1]
                cache[colour] = mapped
            out_px[x, y] = mapped
    return out


def save(img: Image.Image, path: Path, colours: int = 24) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("P", palette=Image.ADAPTIVE, colors=colours).save(path, optimize=True)
    print(f"  {path}  ({path.stat().st_size // 1024} KB, {img.size[0]}x{img.size[1]})")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug", required=True, help="project slug, e.g. simproc")
    ap.add_argument("--input", type=Path, help="local render.png instead of downloading")
    ap.add_argument("--shuttle", help="Tiny Tapeout shuttle, e.g. ttsky25b")
    ap.add_argument("--module", help="top module, e.g. tt_um_ieeeuoftasic_simproc")
    ap.add_argument("--out", type=Path, default=Path("assets/projects"))
    args = ap.parse_args()

    if args.input:
        raw = Image.open(args.input)
    else:
        if not (args.shuttle and args.module):
            ap.error("give --input, or both --shuttle and --module")
        url = RENDER_URL.format(shuttle=args.shuttle, module=args.module)
        print(f"fetching {url}")
        with urllib.request.urlopen(url) as response:  # noqa: S310 - fixed, trusted host
            raw = Image.open(io.BytesIO(response.read()))

    print("re-inking...")
    die = reink(raw)
    width, height = die.size

    print("writing:")
    save(die.resize((760, round(760 * height / width)), Image.LANCZOS), args.out / f"{args.slug}-die.png")

    # Hero. Two constraints pull against each other here:
    #
    #   * the crop must carry enough real layout detail that a full-bleed hero is
    #     not magnified into mush, so take a wide region at native resolution
    #     rather than a small one blown up;
    #   * the finished asset must be wider than the widest realistic hero, so
    #     browsers only ever scale it DOWN. Upscaling a background image is what
    #     makes it look blurry, and `background-size: cover` on a 2560px monitor
    #     will happily magnify a small asset 3x.
    #
    # A whole-number NEAREST upscale keeps the layout's pixel grid crisp instead
    # of smearing it, and compresses well because the blocks are flat.
    crop_w = min(1200, width)
    crop_h = min(round(crop_w / 2.6), height)
    left, top = (width - crop_w) // 2, (height - crop_h) // 2
    hero = die.crop((left, top, left + crop_w, top + crop_h))
    hero = hero.resize((hero.width * HERO_UPSCALE, hero.height * HERO_UPSCALE), Image.NEAREST)
    save(hero, args.out / f"{args.slug}-hero.png")

    og = die.resize((1200, round(1200 * height / width)), Image.LANCZOS).crop((0, 0, 1200, 630))
    save(og, args.out / f"{args.slug}-og.png")

    print(
        f"\nNow point _projects/{args.slug}.md at:\n"
        f"  render: /assets/projects/{args.slug}-die.png\n"
        f"  hero:   /assets/projects/{args.slug}-hero.png"
    )


if __name__ == "__main__":
    main()
