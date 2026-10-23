#!/usr/bin/env python3
"""op55 preview.py: a shareable preview video of a rendered cue. Make one only when the user asks for it.

  python3 preview.py <music.wav> [--meta music.meta.json] [--out music.preview.mp4] [--title "..."]
                     [--size 1920x1080] [--fps 24] [--check]

The frame is the cue's spectrogram with its sections, accents, narration gaps and bar ruler (all from <wav>.meta.json,
written by render.mjs). While the sound plays, a playhead sweeps across: what has played is in colour, what is still to
come is grey. The current section's name and a timecode sit above. --check also writes three still frames (25/50/75 %)
next to the video so you can Read them; you cannot watch the video.

Needs ffmpeg (showspectrumpic, maskedmerge) and Pillow (pip install pillow). Fonts are bundled (assets/fonts, OFL);
Hangul/CJK text falls back to a system font ($OP55_CJK_FONT, Pretendard, Apple SD Gothic Neo, Noto Sans CJK).
"""
import argparse
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps
except ImportError:
    sys.exit("preview.py needs Pillow: python3 -m pip install pillow")

HERE = Path(__file__).resolve().parent
FONTS = HERE.parent / "assets" / "fonts"
INK, IVORY, DIM, FAINT, RED = (10, 9, 8), (239, 230, 214), (169, 157, 138), (111, 102, 86), (255, 59, 31)
CJK_CANDIDATES = [
    *sorted((Path.home() / "Library/Fonts").glob("Pretendard-*.otf")), *sorted(Path("/Library/Fonts").glob("Pretendard-*.otf")),
    Path("/System/Library/Fonts/AppleSDGothicNeo.ttc"),
    *sorted(Path("/usr/share/fonts").glob("**/NotoSansCJK*-Regular.ttc")), *sorted(Path("/usr/share/fonts").glob("**/NotoSansKR*.ttf")),
]


def needs_cjk(s):
    return any("ᄀ" <= c <= "ᇿ" or "　" <= c <= "鿿" or "가" <= c <= "힯" or "＀" <= c <= "￯" for c in s)


_warned = set()


def font(kind, px, text="", weight=400):
    px = max(8, int(round(px)))
    if needs_cjk(text):
        import os
        cands = [Path(os.environ["OP55_CJK_FONT"])] if os.environ.get("OP55_CJK_FONT") else []
        for p in cands + CJK_CANDIDATES:
            if p.exists():
                return ImageFont.truetype(str(p), px)
        if "cjk" not in _warned:
            print("! no Hangul/CJK font found (set OP55_CJK_FONT); those characters will not render", file=sys.stderr)
            _warned.add("cjk")
    if kind == "serif":
        return ImageFont.truetype(str(FONTS / "InstrumentSerif-Italic.ttf"), px)
    f = ImageFont.truetype(str(FONTS / "JetBrainsMono-wght.ttf"), px)
    f.set_variation_by_axes([weight])
    return f


def text_w(f, s):
    return f.getbbox(s)[2] if s else 0


def spaced(s, n=1):
    return (" " * n).join(s)          # letter-spaced caps without a shaping engine


def mmss(t):
    t = max(0, int(t))
    return f"{t // 60}:{t % 60:02d}"


def probe_duration(wav):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(wav)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


class Layout:
    def __init__(self, W, H):
        self.W, self.H, self.u = W, H, min(W / 1920, H / 1080)
        u = self.u
        self.pad = round(80 * u)
        self.sx0, self.sx1 = self.pad, W - self.pad
        self.sw = self.sx1 - self.sx0
        self.title_y = round(0.055 * H)
        self.now_y = round(0.165 * H)
        self.label_y = round(0.232 * H)
        self.row_h = round(30 * self.u)
        self.sy0, self.sy1 = round(0.33 * H), round(0.78 * H)
        self.tri_y = self.sy1 + round(10 * u)
        self.gap_y = self.sy1 + round(34 * u)
        self.rule_y = self.sy1 + round(52 * u)
        self.cap_y = round(0.925 * H)
        self.band = (self.label_y - round(8 * u), self.rule_y + round(14 * u))   # rows that turn from grey to colour


def bar_ticks(grid, dur):
    """[(t, bar index)] for every downbeat inside the file"""
    if not grid or not grid.get("beat"):
        return []
    beat, t0, bpb, fd = grid["beat"], grid.get("t0", 0), grid.get("beatsPerBar", 4), grid.get("firstDownbeat", 0)
    k = math.ceil(((0 - t0) / beat - fd) / bpb - 1e-9)
    out = []
    while True:
        t = t0 + (fd + bpb * k) * beat
        if t > dur:
            return out
        if t >= 0:
            out.append((t, k))
        k += 1


def card(meta, wav, dur, title, L, tmp):
    W, H, u = L.W, L.H, L.u
    x = lambda t: L.sx0 + t / dur * L.sw
    img = Image.new("RGB", (W, H), INK)
    spec = tmp / "spec.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-lavfi",
                    f"showspectrumpic=s={L.sw}x{L.sy1 - L.sy0}:legend=0:fscale=log:start=40:stop=14000:color=magma:drange=72:scale=log",
                    str(spec)], check=True)
    img.paste(Image.open(spec).convert("RGB").resize((L.sw, L.sy1 - L.sy0)), (L.sx0, L.sy0))
    d = ImageDraw.Draw(img, "RGBA")

    # title and facts
    tf = font("serif", 76 * u, title)
    d.text((L.pad, L.title_y), title, font=tf, fill=IVORY)
    grid = meta.get("grid") or {}
    ticks = bar_ticks(grid, dur)
    facts = []
    if meta.get("key"):
        facts.append(str(meta["key"]))
    if grid.get("bpm"):
        facts.append(f"{grid.get('beatsPerBar', 4)}/4  {grid['bpm']:.0f} BPM")
    facts.append(mmss(dur))
    integ = (meta.get("master") or {}).get("integrated")
    if integ is not None:
        facts.append(f"{integ:.1f} LUFS")
    fs = "  ·  ".join(facts).upper()
    ff = font("mono", 22 * u, fs)
    d.text((W - L.pad - text_w(ff, fs), L.title_y + round(26 * u)), fs, font=ff, fill=DIM)

    # sections: a line each, labels packed into up to three rows (first row with room; else trimmed with an ellipsis)
    secs = sorted(meta.get("sections") or [], key=lambda s: s["t"])
    lf = font("mono", 19 * u, " ".join(str(s.get("name", "")) for s in secs), weight=500)
    rows_end = [-1e9, -1e9, -1e9]
    placed = []                                                       # [sx, row, label, flipped, left edge, width]
    for i, s in enumerate(secs):
        sx = x(s["t"])
        lab = f"{i + 1:02d} {str(s.get('name', '')).upper()}"
        lw = text_w(lf, lab)
        flip = sx + 10 * u + lw > L.sx1 + L.pad / 2                    # flip left at the right edge
        left = sx - 7 * u - lw if flip else sx + 7 * u
        r = next((k for k, e in enumerate(rows_end) if left >= e + 8 * u), min(range(3), key=lambda k: rows_end[k]))
        placed.append([sx, r, lab, flip, left, lw])
        rows_end[r] = left + lw
    for j, (sx, r, lab, flip, lx, lw) in enumerate(placed):
        if not flip:                                                   # trim to the next label's left edge in the same row
            nxt = next((q[4] for q in placed[j + 1:] if q[1] == r), L.W - 4 * u)
            room = min(nxt, L.W - 4 * u) - lx - 8 * u
            while len(lab) > 4 and text_w(lf, lab) > room:
                lab = lab[:-2] + "…"
            lw = text_w(lf, lab)
            if lw > room or (lab.endswith("…") and len(lab) < 8):      # unreadable even trimmed: line only
                lab = ""
        ly = L.label_y + r * L.row_h
        d.line([(sx, ly), (sx, L.sy1)], fill=IVORY + (140,), width=max(1, round(u)))
        if lab:
            d.rectangle([lx - 3 * u, ly, lx + lw + 3 * u, ly + 26 * u], fill=INK + (150,))
            d.text((lx, ly + 2 * u), lab, font=lf, fill=IVORY)
    # accents
    for a in meta.get("accents") or []:
        ax, s = x(a["t"]), 8 * u
        d.polygon([(ax - s, L.tri_y + 1.7 * s), (ax + s, L.tri_y + 1.7 * s), (ax, L.tri_y)], fill=RED)
    # narration-free gaps
    for g0, g1 in meta.get("gaps") or []:
        d.rectangle([x(g0), L.gap_y, x(g1), L.gap_y + 5 * u], fill=IVORY + (110,))
    # ruler: bars if the grid is known, else seconds
    rf = font("mono", 15 * u, "0")
    marks = ticks or [(float(t), t) for t in range(0, int(dur) + 1)]
    step = next((s for s in (1, 2, 4, 5, 8, 10, 16, 20, 25, 50, 100, 200) if s * L.sw / max(1, len(marks)) >= 64 * u), 500)
    for t, k in marks:
        mx = x(t)
        big = k % step == 0
        d.line([(mx, L.rule_y), (mx, L.rule_y + (12 if big else 6) * u)], fill=DIM if big else FAINT, width=max(1, round(u)))
        if big:
            d.text((mx - text_w(rf, str(k)) / 2, L.rule_y + 16 * u), str(k), font=rf, fill=DIM)
    cap = f"op55  ·  {Path(wav).name}  ·  spectrogram of the render  ·  ruler = {'bars' if ticks else 'seconds'}"
    cap += ("  ·  red = accents" if meta.get("accents") else "") + ("  ·  light band = narration gaps" if meta.get("gaps") else "")
    cf = font("mono", 15 * u, cap)
    d.text((L.pad, L.cap_y), cap.upper(), font=cf, fill=FAINT)

    grey = img.copy()
    b0, b1 = L.band
    region = grey.crop((0, b0, W, b1))
    region = ImageEnhance.Brightness(ImageOps.grayscale(region).convert("RGB")).enhance(0.82)
    grey.paste(region, (0, b0))
    return img, grey


def overlays(meta, dur, L, tmp):
    """now-playing strips (one per section) and a 1-fps timecode sequence"""
    u = L.u
    nf = font("mono", 30 * u, " ".join(s.get("name", "") for s in meta.get("sections") or []), weight=600)
    hgt = round(46 * u)
    secs = sorted(meta.get("sections") or [], key=lambda s: s["t"])
    strips = []
    for i, s in enumerate(secs):
        im = Image.new("RGBA", (round(L.W * 0.6), hgt), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        r = 7 * u
        d.ellipse([L.pad, hgt / 2 - r, L.pad + 2 * r, hgt / 2 + r], fill=RED)
        d.text((L.pad + 4 * r, hgt / 2 - 19 * u), f"NOW   {i + 1:02d} {str(s.get('name', '')).upper()}", font=nf, fill=IVORY)
        p = tmp / f"now_{i:03d}.png"
        im.save(p)
        t1 = secs[i + 1]["t"] if i + 1 < len(secs) else dur + 1
        strips.append((p, s["t"], t1))
    cf = font("mono", 30 * u, "0", weight=500)
    cw = round(text_w(cf, "00:00 / 00:00") + 8 * u)
    (tmp / "tc").mkdir(exist_ok=True)
    for sec in range(int(math.ceil(dur)) + 1):
        im = Image.new("RGBA", (cw, hgt), (0, 0, 0, 0))
        s = f"{mmss(sec)} / {mmss(dur)}"
        ImageDraw.Draw(im).text((cw - text_w(cf, s), hgt / 2 - 19 * u), s, font=cf, fill=DIM)
        im.save(tmp / "tc" / f"{sec:05d}.png")
    return strips, (L.W - L.pad - cw, L.now_y), hgt


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("wav")
    ap.add_argument("--meta")
    ap.add_argument("--out")
    ap.add_argument("--title")
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--abr", default="160k", help="AAC bitrate (default 160k)")
    ap.add_argument("--check", action="store_true", help="also write stills at 25/50/75 %% next to the video")
    a = ap.parse_args()
    wav = Path(a.wav).resolve()
    meta_p = Path(a.meta) if a.meta else wav.with_name(wav.stem + ".meta.json")
    meta = json.loads(meta_p.read_text()) if meta_p.exists() else {}
    if not meta:
        print(f"! {meta_p} not found: no sections, accents or bar ruler (render with render.mjs to get them)", file=sys.stderr)
    out = Path(a.out).resolve() if a.out else wav.with_name(wav.stem + ".preview.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    W, H = (int(v) for v in a.size.lower().split("x"))
    W, H = W - W % 2, H - H % 2
    dur = probe_duration(wav)
    title = a.title or meta.get("title") or wav.stem
    L = Layout(W, H)

    with tempfile.TemporaryDirectory(dir=out.parent, prefix=".preview-") as td:
        tmp = Path(td)
        colour, grey = card(meta, wav, dur, title, L, tmp)
        colour.save(tmp / "colour.png"); grey.save(tmp / "grey.png")
        strips, (tcx, tcy), hgt = overlays(meta, dur, L, tmp)
        b0, b1 = L.band
        X = f"{L.sx0}+t/{dur:.6f}*{L.sw}"
        f = a.fps
        inputs = ["-loop", "1", "-framerate", str(f), "-i", str(tmp / "colour.png"),
                  "-loop", "1", "-framerate", str(f), "-i", str(tmp / "grey.png"),
                  "-i", str(wav), "-framerate", "1", "-i", str(tmp / "tc" / "%05d.png")]
        for p, _, _ in strips:
            inputs += ["-loop", "1", "-framerate", str(f), "-i", str(p)]
        g = [f"[0:v]format=gbrp[c]", f"[1:v]format=gbrp[g]",
             f"color=c=black:s={W}x{H}:r={f},format=gbrp[m0]", f"color=c=white:s={L.sw}x{b1 - b0}:r={f},format=gbrp[w]",
             f"[m0][w]overlay=x='{X}-{L.sw}':y={b0}:eval=frame:format=gbrp[mask]",
             f"[g][c][mask]maskedmerge[mm]",
             f"color=c=white@0.95:s={max(2, round(2 * L.u))}x{b1 - L.sy0}:r={f},format=rgba[bar]",     # starts below the label rows
             f"[mm][bar]overlay=x='{X}':y={L.sy0}:eval=frame[v0]",
             f"[v0][3:v]overlay=x={tcx}:y={tcy}:eof_action=repeat[v1]"]
        cur = "v1"
        for i, (_, t0, t1) in enumerate(strips):
            g.append(f"[{cur}][{4 + i}:v]overlay=x=0:y={L.now_y}:enable='gte(t,{t0:.3f})*lt(t,{t1:.3f})'[s{i}]")
            cur = f"s{i}"
        g.append(f"[{cur}]format=yuv420p[vout]")
        cmd = ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(g), "-map", "[vout]", "-map", "2:a",
               "-t", f"{dur:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "24", "-tune", "stillimage", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", a.abr, "-movflags", "+faststart", str(out)]
        subprocess.run(cmd, check=True)
    size = out.stat().st_size / 1048576
    print(f"{out}  ({W}x{H}, {dur:.1f} s, {size:.1f} MB)")
    if size > 10:
        print("  over GitHub's 10 MB attachment limit: try --size 1280x720 --fps 12 --abr 128k")
    if a.check:
        for frac in (0.25, 0.5, 0.75):
            p = out.with_name(f"{out.stem}.check{int(frac * 100)}.jpg")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{dur * frac:.3f}", "-i", str(out), "-frames:v", "1", str(p)], check=True)
            print(f"  still {int(frac * 100)}% ({dur * frac:.1f} s): {p}")


if __name__ == "__main__":
    main()
