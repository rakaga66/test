#!/usr/bin/env python3
"""Make Doran (a Persian-style font) read as Arabic: adds the inner mark to isolated/final
kaf (ك instead of ک) and the two dots under isolated/final yeh (ي instead of ی).
Writes fonts/doran-ar.ttf next to the original; the original file is not touched.
Usage: python3 scripts/arabize_font.py [--kaf X Y S] [--yeh X Y]
"""
import pathlib, sys
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.boundsPen import BoundsPen

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "fonts" / "doran-fanum-extrabold.ttf"
OUT = ROOT / "fonts" / "doran-ar.ttf"

# mark placement, in font units (em = 2000), measured from each glyph's left edge
KAF = {"u0643": (590, 640, 0.78), "uFEDA": (610, 640, 0.78)}
YEH = {"u064A": (660, -800), "uFEF2": (760, -830)}


def contours(gs, name):
    rp = DecomposingRecordingPen(gs)
    gs[name].draw(rp)
    out, cur = [], []
    for op, args in rp.value:
        cur.append((op, args))
        if op in ("closePath", "endPath"):
            out.append(cur)
            cur = []
    return out


def bounds(gs, ops):
    bp = BoundsPen(gs)
    for op, args in ops:
        getattr(bp, op)(*args)
    return bp.bounds


def rebuild(font, gs, name, extra, tx, ty, s):
    pen = TTGlyphPen(gs)
    gs[name].draw(pen)
    tp = TransformPen(pen, (s, 0, 0, s, tx, ty))
    for op, args in extra:
        getattr(tp, op)(*args)
    g = pen.glyph()
    font["glyf"][name] = g
    g.recalcBounds(font["glyf"])


def main():
    f = TTFont(str(SRC))
    gs = f.getGlyphSet()
    hamza = [op for c in contours(gs, "u0654") for op in c]
    hb = bounds(gs, hamza)
    dots_c = min(contours(gs, "uFEF3"), key=lambda c: (lambda b: (b[2] - b[0]) * (b[3] - b[1]))(bounds(gs, c)))
    db = bounds(gs, dots_c)
    for name, (x, y, s) in KAF.items():
        # centre the hamza-like mark at (x, y)
        cx, cy = (hb[0] + hb[2]) / 2 * s, (hb[1] + hb[3]) / 2 * s
        rebuild(f, gs, name, hamza, x - cx, y - cy, s)
    for name, (x, y) in YEH.items():
        cx, cy = (db[0] + db[2]) / 2, (db[1] + db[3]) / 2
        rebuild(f, gs, name, dots_c, x - cx, y - cy, 1.0)
    for t in ("name",):
        for rec in f[t].names:
            if rec.nameID in (1, 4):
                rec.string = "Doran AR"
            if rec.nameID == 6:
                rec.string = "DoranAR-ExtraBold"
    f.save(str(OUT))
    print("wrote", OUT)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--kaf"]:
        x, y, s = map(float, args[1:4])
        KAF = {"u0643": (x, y, s), "uFEDA": (x + 20, y, s)}
    main()
