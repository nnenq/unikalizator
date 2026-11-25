"""Documentary engine (rebuilt). Calm motion-graphics renderer: photos, quotes, dials, maps, boards.
Usage from a project dir containing script.py, plan.py, img/, vo/:
    python3 dk.py info | shots [keys..] | range i0 i1 out.mp4 | srt out.srt
"""
import os, sys, json, math, random, re, importlib.util
import cairo
import numpy as np
from PIL import Image, ImageFilter, ImageOps

W, H, FPS = 1920, 1080, 30
PROJ = os.getcwd()
ENG = os.path.dirname(os.path.abspath(__file__))

def hx(s):
    s = s.lstrip('#'); return tuple(int(s[i:i + 2], 16) / 255 for i in (0, 2, 4))
BG, AMB, RED, WHITE, GREY, PAPER, INK = hx('141416'), hx('d9a441'), hx('b3302a'), hx('f2f0ea'), hx('8a8a8a'), hx('e9e4d8'), hx('1d1b18')
LAND, EDGE, SEA, HL = hx('2a2c30'), hx('45484e'), hx('101418'), hx('8e2a24')

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def seg(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def lerp(a, b, k): return a + (b - a) * k
def src(ctx, c, a=1.0): ctx.set_source_rgba(c[0], c[1], c[2], a)

# ---------------------------------------------------------------- text
FONTS = {'head': 'Bebas Neue', 'type': 'Special Elite', 'sub': 'Oswald', 'mono': 'PT Mono'}
TR = str.maketrans('ŁłĘęŃńŚśŻżŹźĄąĆć', 'LlEeNnSsZzZzAaCc')

def font(ctx, f, size, bold=False):
    ctx.select_font_face(FONTS.get(f, f), cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)

def tw(ctx, s, size, f='head', bold=False):
    font(ctx, f, size, bold); return ctx.text_extents(s.translate(TR)).x_advance

def txt(ctx, s, x, y, size, f='head', col=WHITE, a=1.0, align='c', shadow=True, bold=False):
    if a <= 0 or not s: return
    s = s.translate(TR); font(ctx, f, size, bold)
    w = ctx.text_extents(s).x_advance
    x0 = x - w / 2 if align == 'c' else (x - w if align == 'r' else x)
    if shadow:
        ctx.move_to(x0 + 3, y + 4); src(ctx, (0, 0, 0), 0.55 * a); ctx.show_text(s)
    ctx.move_to(x0, y); src(ctx, col, a); ctx.show_text(s)
    return w

def rrect(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()

def line(ctx, a, b, w, col, al=1.0):
    ctx.move_to(*a); ctx.line_to(*b); ctx.set_line_width(w); src(ctx, col, al); ctx.stroke()

def tag(ctx, s, x, y, size=24, a=1.0):
    s = s.translate(TR); font(ctx, 'mono', size); w = ctx.text_extents(s).x_advance
    ctx.rectangle(x, y, w + 24, size + 16); src(ctx, PAPER, 0.85 * a); ctx.fill()
    ctx.move_to(x + 12, y + size + 4); src(ctx, INK, a); ctx.show_text(s)

def stamp(ctx, s, x, y, size, k, rot=-0.12, col=RED):
    if k <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); sc = lerp(1.6, 1.0, ease_out(k)); ctx.scale(sc, sc)
    font(ctx, 'head', size); s = s.translate(TR); w = ctx.text_extents(s).x_advance; spc = size * 0.12
    w += spc * (len(s) - 1)
    rrect(ctx, -w / 2 - 18, -size * 0.85, w + 36, size * 1.15, 6); ctx.set_line_width(5); src(ctx, col, 0.9 * k); ctx.stroke()
    xx = -w / 2
    for ch in s:
        ctx.move_to(xx, size * 0.12); src(ctx, col, 0.9 * k); ctx.show_text(ch); xx += ctx.text_extents(ch).x_advance + spc
    ctx.restore()

def typed(s, t, cps=30):
    n = int(max(0, t) * cps); return s[:n]

# ---------------------------------------------------------------- images
_IMG = {}
def photo(name, blur=0):
    key = (name, blur)
    if key in _IMG: return _IMG[key]
    p = os.path.join(PROJ, 'img', name + '.jpg')
    im = Image.open(p).convert('RGB')
    if max(im.size) > 2600: im.thumbnail((2600, 2600))
    g = ImageOps.grayscale(im)
    g = ImageOps.autocontrast(g, cutoff=1)
    if blur: g = g.filter(ImageFilter.GaussianBlur(blur))
    arr = np.asarray(g).astype(np.float32) / 255.0
    # warm monochrome grade
    r = np.clip(arr * 1.02 + 0.015, 0, 1); gg = np.clip(arr * 0.97 + 0.01, 0, 1); b = np.clip(arr * 0.88, 0, 1)
    rgb = (np.dstack([b, gg, r, np.ones_like(arr)]) * 255).astype(np.uint8)  # BGRA for cairo
    h, w = arr.shape
    stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_ARGB32, w)
    buf = np.zeros((h, stride // 4, 4), np.uint8); buf[:, :w] = rgb
    surf = cairo.ImageSurface.create_for_data(bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, w, h, stride)
    _IMG[key] = surf
    return surf

def cover(ctx, surf, z=1.0, fx=0.5, fy=0.5, a=1.0, box=(0, 0, W, H)):
    x, y, bw, bh = box
    iw, ih = surf.get_width(), surf.get_height()
    s = max(bw / iw, bh / ih) * z
    ox = x + (bw - iw * s) * fx; oy = y + (bh - ih * s) * fy
    ctx.save(); ctx.rectangle(x, y, bw, bh); ctx.clip()
    ctx.translate(ox, oy); ctx.scale(s, s); ctx.set_source_surface(surf, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_GOOD); ctx.paint_with_alpha(a); ctx.restore()

def u_of(t, d): return clamp(t / max(d, 0.1))

def bgphoto(ctx, p, t, d, dim=0.72, blur=0):
    src(ctx, BG); ctx.paint()
    if p.get('bgimg') and p['bgimg'] != 'dark':
        cover(ctx, photo(p['bgimg'], blur), lerp(1.05, 1.13, u_of(t, d)))
        ctx.rectangle(0, 0, W, H); src(ctx, BG, dim); ctx.fill()

# grain & vignette
_GR = []
def grain(ctx, t):
    if not _GR:
        rnd = np.random.default_rng(3)
        for i in range(6):
            n = (rnd.random((270, 480)) * 255).astype(np.uint8)
            a = np.dstack([n, n, n, np.full_like(n, 255)])
            stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_ARGB32, 480)
            _GR.append(cairo.ImageSurface.create_for_data(bytearray(a.tobytes()), cairo.FORMAT_ARGB32, 480, 270, stride))
    g = _GR[int(t * 12) % len(_GR)]
    ctx.save(); ctx.scale(4, 4); ctx.set_source_surface(g, 0, 0); ctx.get_source().set_filter(cairo.FILTER_NEAREST)
    ctx.set_operator(cairo.OPERATOR_OVERLAY); ctx.paint_with_alpha(0.10); ctx.restore()
    rg = cairo.RadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 1.0)
    rg.add_color_stop_rgba(0, 0, 0, 0, 0); rg.add_color_stop_rgba(1, 0, 0, 0, 0.6)
    ctx.set_source(rg); ctx.paint()

def grid_bg(ctx, t):
    src(ctx, BG); ctx.paint()
    ctx.set_line_width(1); src(ctx, (1, 1, 1), 0.025)
    for x in range(0, W, 60): ctx.move_to(x, 0); ctx.line_to(x, H)
    for y in range(0, H, 60): ctx.move_to(0, y); ctx.line_to(W, y)
    ctx.stroke()

# ---------------------------------------------------------------- visuals
AUTOTAG = {}

def v_photo(ctx, t, d, p):
    src(ctx, BG); ctx.paint()
    u = u_of(t, d); z0, z1 = p.get('z0', 1.0), p.get('z1', 1.12)
    f0 = p.get('f0', (0.5, 0.5)); f1 = p.get('f1', f0)
    cover(ctx, photo(p['img']), lerp(z0, z1, ease(u)), lerp(f0[0], f1[0], u), lerp(f0[1], f1[1], u))
    tg = p.get('tag') or AUTOTAG.get(p['img'])
    if tg: tag(ctx, tg, 60, 50, 22, ease(seg(t, 0.3, 0.9)))

def _hlrun(ctx, x, y, s, size, a, hl):
    """draw words; hl=True -> red box behind."""
    w = tw(ctx, s, size)
    if hl:
        rrect(ctx, x - 10, y - size * 0.82, w + 20, size * 1.02, 4); src(ctx, RED, 0.95 * a); ctx.fill()
    txt(ctx, s, x, y, size, col=WHITE, a=a, align='l', shadow=not hl)
    return w

def v_quote(ctx, t, d, p):
    bgphoto(ctx, p, t, d, 0.78, blur=2)
    lines = p['lines']; size = p.get('size', 92 if max(len(l) for l in lines) < 22 else 76)
    y0 = H / 2 - (len(lines) - 1) * size * 0.6 + size * 0.3
    for j, ln in enumerate(lines):
        a = ease(seg(t, 0.15 + j * 0.35, 0.65 + j * 0.35))
        parts = re.split(r'(\*[^*]*$|\*\S+)', ln) if '*' in ln else [ln]
        segs = []
        for ptx in parts:
            if not ptx: continue
            if ptx.startswith('*'): segs.append((ptx[1:], True))
            else: segs.append((ptx, False))
        total = sum(tw(ctx, s, size) for s, _ in segs) + 14 * sum(1 for _, h in segs if h)
        x = W / 2 - total / 2; y = y0 + j * size * 1.2
        for s, h in segs:
            if h and s.startswith(' '): x += tw(ctx, ' ', size); s = s.lstrip()
            x += _hlrun(ctx, x + (7 if h else 0), y, s, size, a, h) + (14 if h else 0)

def v_dial(ctx, t, d, p):
    bgphoto(ctx, p, t, d, 0.8)
    items = p['items']; n = len(items); vs = p.get('vs', False)
    xs = [W / 2] if n == 1 else [W * 0.3, W * 0.7]
    if n == 1: xs = [W * 0.32]
    for i, it in enumerate(items):
        big, lab, col = it[0], it[1], hx(it[2]) if isinstance(it[2], str) else it[2]
        a = ease(seg(t, 0.2 + i * 0.5, 0.7 + i * 0.5))
        size = 150 if len(big) <= 9 else (110 if len(big) <= 14 else 84)
        if n == 1 and tw(ctx, big, size) > 1100: size = int(size * 1100 / tw(ctx, big, size))
        if n == 2 and tw(ctx, big, size) > 760: size = int(size * 760 / tw(ctx, big, size))
        txt(ctx, big, xs[i], H / 2 + size * 0.3, size, col=col, a=a)
        if lab: txt(ctx, lab.upper(), xs[i], H / 2 + size * 0.3 + 60, 30, f='type', col=GREY if n == 2 else PAPER, a=a, shadow=False)
    if n == 2 and vs: txt(ctx, 'VS', W / 2, H / 2 + 20, 44, col=GREY, a=ease(seg(t, 0.5, 0.9)))

def v_counter(ctx, t, d, p):
    bgphoto(ctx, p, t, d, 0.82)
    k = ease_out(seg(t, 0.2, min(d * 0.6, 2.6)))
    val = lerp(p.get('a', 0), p['b'], k)
    s = p.get('fmt', '{:,.0f}').format(val)
    txt(ctx, s, W / 2, H / 2 + 40, 200, col=AMB)
    txt(ctx, p['label'].upper(), W / 2, H / 2 + 120, 40, f='type', col=PAPER, a=ease(seg(t, 0.4, 0.9)), shadow=False)
    if p.get('sub'): txt(ctx, p['sub'].upper(), W / 2, H / 2 + 170, 26, f='type', col=GREY, a=ease(seg(t, 0.7, 1.2)), shadow=False)

def torn_panel(ctx, x0, k):
    ctx.move_to(W, 0); ctx.line_to(x0, 0)
    rnd = random.Random(7); y = 0
    while y < H:
        y += 24; ctx.line_to(x0 + rnd.uniform(-9, 9), y)
    ctx.line_to(W, H); ctx.close_path()
    src(ctx, hx('17171a'), 0.97 * k); ctx.fill_preserve(); ctx.set_line_width(3); src(ctx, RED, 0.8 * k); ctx.stroke()

def v_list(ctx, t, d, p):
    src(ctx, BG); ctx.paint()
    if p.get('img') and p['img'] != 'dark':
        cover(ctx, photo(p['img']), lerp(1.05, 1.12, u_of(t, d)), box=(0, 0, W, H))
        ctx.rectangle(0, 0, W, H); src(ctx, BG, 0.25); ctx.fill()
    else:
        grid_bg(ctx, t)
    k = ease_out(seg(t, 0, 0.5)); x0 = lerp(W, W * 0.5, k)
    torn_panel(ctx, x0, 1.0)
    items = p['items']; head = p['head']
    size = 40 if len(items) <= 4 else 34
    txt(ctx, head.upper(), x0 + 70, 330, 48, col=RED, a=ease(seg(t, 0.3, 0.7)), align='l', shadow=False)
    for j, it in enumerate(items):
        it = it.lstrip('*')
        a = ease(seg(t, 0.6 + j * 0.45, 1.0 + j * 0.45))
        y = 410 + j * 74
        ctx.arc(x0 + 82, y - 12, 7, 0, 2 * math.pi); src(ctx, RED, a); ctx.fill()
        txt(ctx, typed(it.upper(), t - 0.6 - j * 0.45, 40), x0 + 108, y, size * 0.8, f='type', col=PAPER, a=a, align='l', shadow=False)

def v_doc(ctx, t, d, p):
    grid_bg(ctx, t)
    k = ease_out(seg(t, 0, 0.6))
    cw, ch = 1100, 640; cx, cy = W / 2 - cw / 2, lerp(H, H / 2 - ch / 2 - 20, k)
    ctx.save(); ctx.translate(W / 2, cy + ch / 2); ctx.rotate(-0.012); ctx.translate(-W / 2, -(cy + ch / 2))
    ctx.rectangle(cx + 10, cy + 14, cw, ch); src(ctx, (0, 0, 0), 0.5); ctx.fill()
    ctx.rectangle(cx, cy, cw, ch); src(ctx, PAPER); ctx.fill()
    txt(ctx, p['head'].upper(), cx + 60, cy + 90, 34, f='mono', col=INK, align='l', shadow=False)
    line(ctx, (cx + 60, cy + 115), (cx + cw - 60, cy + 115), 2, INK, 0.7)
    for j, ln in enumerate(p['lines']):
        hl = ln.startswith('*'); s = ln.lstrip('*').upper()
        ss = typed(s, t - 0.8 - j * 1.0, 32); y = cy + 200 + j * 80
        size = 40 if len(s) < 34 else 32
        if hl and ss:
            w = tw(ctx, ss, size, 'mono'); ctx.rectangle(cx + 52, y - size * 0.85, w + 16, size * 1.15); src(ctx, RED, 0.85); ctx.fill()
        txt(ctx, ss, cx + 60, y, size, f='mono', col=WHITE if hl else INK, align='l', shadow=False)
    ctx.restore()

def v_title(ctx, t, d, p):
    bgphoto(ctx, p, t, d, 0.8)
    size = p.get('size', 140); a = ease(seg(t, 0.1, 0.6))
    if tw(ctx, p['title'], size) > 1700: size = int(size * 1700 / tw(ctx, p['title'], size))
    txt(ctx, p['title'], W / 2, H / 2 + 10, size, col=AMB, a=a)
    line(ctx, (W / 2 - 300 * ease(seg(t, 0.4, 1.0)), H / 2 + 45), (W / 2 + 300 * ease(seg(t, 0.4, 1.0)), H / 2 + 45), 3, AMB, 0.8)
    if p.get('sub'): txt(ctx, p['sub'].upper(), W / 2, H / 2 + 105, 34, f='type', col=PAPER, a=ease(seg(t, 0.6, 1.1)), shadow=False)

def v_chapter(ctx, t, d, p):
    bgphoto(ctx, p, t, d, 0.84, blur=3)
    a = ease(seg(t, 0.1, 0.6)) * (1 - ease(seg(t, d - 0.6, d)))
    txt(ctx, f"CHAPTER {p['num']:02d}", W / 2, H / 2 - 50, 40, col=RED, a=a, shadow=False)
    txt(ctx, p['title'], W / 2, H / 2 + 50, 96, f='type', col=WHITE, a=a)

# ---------------------------------------------------------------- maps
_TOPO = None
def countries():
    global _TOPO
    if _TOPO is None:
        tj = json.load(open(os.path.join(ENG, 'countries-50m.json')))
        sc, tr = tj['transform']['scale'], tj['transform']['translate']
        arcs = []
        for arc in tj['arcs']:
            x = y = 0; pts = []
            for dx, dy in arc:
                x += dx; y += dy; pts.append((x * sc[0] + tr[0], y * sc[1] + tr[1]))
            arcs.append(pts)
        def ring(ids):
            out = []
            for i in ids:
                pts = arcs[i] if i >= 0 else arcs[~i][::-1]
                out.extend(pts if not out else pts[1:])
            return out
        C = {}
        for g in tj['objects']['countries']['geometries']:
            nm = g.get('properties', {}).get('name', '')
            polys = []
            if g['type'] == 'Polygon': polys = [[ring(r) for r in g['arcs']]]
            elif g['type'] == 'MultiPolygon': polys = [[ring(r) for r in pg] for pg in g['arcs']]
            C[nm] = polys
        _TOPO = C
    return _TOPO

def merc(lo, la): return lo, math.degrees(math.log(math.tan(math.pi / 4 + math.radians(clamp(la, -85, 85)) / 2)))

class View:
    def __init__(self, box, zoom=1.0):
        lo0, lo1, la0, la1 = box; cx, cy = (lo0 + lo1) / 2, (la0 + la1) / 2
        hw, hh = (lo1 - lo0) / 2 / zoom, (la1 - la0) / 2 / zoom
        self.x0, self.y1 = merc(cx - hw, cy + hh); self.x1, self.y0 = merc(cx + hw, cy - hh)
        self.s = max(W / (self.x1 - self.x0), H / (self.y1 - self.y0))
        self.ox = (W - (self.x1 - self.x0) * self.s) / 2; self.oy = (H - (self.y1 - self.y0) * self.s) / 2
        self.east = lo0 > 0
    def p(self, lo, la):
        if self.east and lo < -150: lo += 360
        x, y = merc(lo, la); return self.ox + (x - self.x0) * self.s, self.oy + (self.y1 - y) * self.s

VIEWS = {}
CITIES = {}

def draw_map(ctx, view, hl, k):
    src(ctx, SEA); ctx.paint()
    for nm, polys in countries().items():
        col = LAND if nm != hl else tuple(lerp(LAND[i], HL, k) for i, _ in enumerate(LAND)) if False else (tuple(lerp(LAND[i], HL[i], k) for i in range(3)) if nm == hl else LAND)
        for pg in polys:
            for r in pg:
                pts = [view.p(lo, la) for lo, la in r]
                if max(q[0] for q in pts) < -50 or min(q[0] for q in pts) > W + 50: continue
                if max(q[1] for q in pts) < -50 or min(q[1] for q in pts) > H + 50: continue
                ctx.move_to(*pts[0])
                for q in pts[1:]: ctx.line_to(*q)
                ctx.close_path()
        src(ctx, col); ctx.fill_preserve(); src(ctx, EDGE); ctx.set_line_width(1.2); ctx.stroke()

def v_geo(ctx, t, d, p):
    z = p.get('zoom', (1.0, 1.1)); zoom = lerp(z[0], z[1], ease(u_of(t, d)))
    view = View(VIEWS[p.get('view')], zoom)
    draw_map(ctx, view, p.get('hl'), ease(seg(t, 0.2, 1.0)))
    for j, (key, lab, dx, dy) in enumerate(p.get('cities', [])):
        x, y = view.p(*CITIES[key]); main = key == p.get('main')
        a = ease(seg(t, 0.4 + j * 0.3, 0.8 + j * 0.3))
        r = 11 if main else 7
        if main:
            pr = (t * 1.2) % 1.0; ctx.arc(x, y, r + 26 * pr, 0, 2 * math.pi); src(ctx, AMB, 0.6 * (1 - pr) * a); ctx.set_line_width(3); ctx.stroke()
        ctx.arc(x, y, r, 0, 2 * math.pi); src(ctx, AMB if main else WHITE, a); ctx.fill()
        txt(ctx, lab, x + dx, y + dy, 40 if main else 28, col=AMB if main else WHITE, a=a, align='l')
    txt(ctx, 'MAP DATA: NATURAL EARTH', W - 50, H - 30, 18, f='mono', col=GREY, align='r', shadow=False)

# ---------------------------------------------------------------- boards
def v_hboard(ctx, t, d, p):
    grid_bg(ctx, t)
    items = p['items']; st = p.get('st', {}); new = set(p.get('new', [])); hl = set(p.get('hl', []))
    txt(ctx, p.get('title', "HAITI'S GANG LEADERS"), W / 2, 110, 62, a=ease(seg(t, 0, 0.4)))
    cols = 4; x0, y0, bw, bh, gx, gy = 130, 160, 390, 200, 30, 22
    LAB = {'D': ('DEAD?', WHITE), 'C': ('U.S. PRISON', RED), 'S': ('HOUSE STRUCK', AMB)}
    for i, (al, role) in enumerate(items):
        c, r = i % cols, i // cols; x = x0 + c * (bw + gx); y = y0 + r * (bh + gy)
        k = ease_out(seg(t, 0.05 + i * 0.03, 0.4 + i * 0.03))
        if k <= 0: continue
        s = st.get(i); dim = 0.45 if (hl and i not in hl) else 1.0
        rrect(ctx, x, y, bw, bh, 10); src(ctx, hx('1a1a1d'), 0.95 * k); ctx.fill_preserve()
        col = RED if i in hl else (GREY if s else AMB)
        src(ctx, col, 0.9 * k * dim); ctx.set_line_width(4 if i in hl else 2); ctx.stroke()
        txt(ctx, f'{i + 1:02d}', x + 22, y + 36, 26, col=GREY, a=k * dim, align='l', shadow=False)
        fs = 48 if len(al) <= 12 else 38
        txt(ctx, al, x + bw / 2, y + 112, fs, a=k * dim, shadow=False)
        if not s: txt(ctx, role, x + bw / 2, y + 160, 22, f='type', col=GREY, a=k * dim, shadow=False)
        else:
            kk = seg(t, p.get('stamp_t', 1.0), p.get('stamp_t', 1.0) + 0.35) if i in new else 1.0
            lab, cc = LAB[s]; stamp(ctx, lab, x + bw / 2, y + 162, 38, kk * dim + (0 if dim == 1 else 0), rot=-0.06, col=cc)
    if p.get('count', True):
        n = len(items); cnt = {v: sum(1 for q in st.values() if q == v) for v in 'DCS'}
        free = n - sum(cnt.values())
        txt(ctx, f"U.S. PRISON {cnt['C']}  ·  DEAD? {cnt['D']}  ·  HOUSE STRUCK {cnt['S']}  ·  AT LARGE / UNKNOWN {free}", W / 2, 905, 38, col=AMB, a=ease(seg(t, 0.8, 1.3)))

def v_fugitive(ctx, t, d, p):
    grid_bg(ctx, t)
    k = ease_out(seg(t, 0, 0.45)); x0 = 260
    rrect(ctx, x0 - 60, 190, 1520, 700, 14); src(ctx, hx('18181b'), 0.95 * k); ctx.fill()
    txt(ctx, p.get('num', ''), x0, 300, 60, col=GREY, a=k, align='l')
    size = 150 if len(p['alias']) <= 11 else 110
    txt(ctx, p['alias'], x0, 440, size, a=k, align='l')
    line(ctx, (x0, 480), (x0 + 900 * ease(seg(t, 0.3, 0.9)), 480), 6, RED)
    if p.get('name'): txt(ctx, p['name'], x0, 545, 40, f='type', col=PAPER, a=ease(seg(t, 0.4, 0.8)), align='l', shadow=False)
    for j, ln in enumerate(p.get('lines', [])):
        txt(ctx, ln, x0, 640 + j * 62, 46, col=AMB if j == 0 else WHITE, a=ease(seg(t, 0.7 + j * 0.25, 1.1 + j * 0.25)), align='l')
    if p.get('stamp'):
        stamp(ctx, p['stamp'], 1420, 420, 92, seg(t, p.get('stamp_t', 1.6), p.get('stamp_t', 1.6) + 0.35), rot=-0.14, col=WHITE if p['stamp'] == 'DEAD' else RED)

KINDS = dict(photo=v_photo, plain=v_photo, quote=v_quote, dial=v_dial, counter=v_counter, list=v_list, doc=v_doc,
             title=v_title, chapter=v_chapter, geo=v_geo, hboard=v_hboard, fugitive=v_fugitive)

# ---------------------------------------------------------------- timeline
def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(PROJ, name + '.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

CFG = load('plan'); PLAN = CFG.PLAN
AUTOTAG.update(getattr(CFG, 'AUTOTAG', {})); VIEWS.update(getattr(CFG, 'VIEWS', {})); CITIES.update(getattr(CFG, 'CITIES', {}))
EXTRA = getattr(CFG, 'EXTRA', {}); SEGROLL = getattr(CFG, 'SEGROLL', {}); ROLL = getattr(CFG, 'ROLL', ['dark'])
LEAD, GAP, CH_EXTRA, TAIL = 0.6, 1.3, 3.5, 3.5
VO = json.load(open(os.path.join(PROJ, 'vo', 'vo.json')))
LINES = VO['lines']; DURS = VO['durs']

def build():
    shots, subs, starts = [], [], []
    tcur = LEAD; rc = 0
    for i, ((key, kind, text), du) in enumerate(zip(LINES, DURS)):
        starts.append(tcur)
        slot = du + (CH_EXTRA if kind == 'chapter' else GAP) + EXTRA.get(key, 0)
        if i == len(LINES) - 1: slot += TAIL
        vis = list(PLAN.get(key, []))
        if not vis: vis = [(1, 'plain', dict(img=ROLL[0]))]
        cap = 6.0 if key.startswith('o') else 8.5
        roll = SEGROLL.get(key[0], ROLL)
        while slot / sum(v[0] for v in vis) > cap and kind != 'chapter':
            im = roll[rc % len(roll)]; rc += 1
            vis.append((1, 'plain', dict(img=im, z0=1.02, z1=1.12)))
        tw_ = sum(v[0] for v in vis); t0 = tcur if i else 0.0
        for w, k, pp in vis:
            ln = slot * w / tw_ + (LEAD if (i == 0 and t0 == 0.0) else 0)
            shots.append(dict(key=key, kind=k, p=pp, t0=t0, t1=t0 + ln)); t0 += ln
        # subtitles
        if kind != 'chapter':
            words = text.split(); chunks, cur = [], ''
            for w_ in words:
                if len(cur) + len(w_) + 1 > 40 and cur: chunks.append(cur); cur = w_
                else: cur = (cur + ' ' + w_).strip()
            chunks.append(cur)
            tot = sum(len(c) for c in chunks); tt = tcur
            for c in chunks:
                dd = du * len(c) / tot; subs.append((tt, tt + dd, c)); tt += dd
        tcur += slot
    shots[-1]['t1'] = tcur
    return shots, subs, starts, tcur

SHOTS, SUBS, STARTS, TOTAL = build()
XF = 0.35

def sub_at(t):
    for a, b, c in SUBS:
        if a <= t < b: return c
    return None

def draw_sub(ctx, s):
    s = s.upper(); words = s.split()
    lng = max(range(len(words)), key=lambda i: len(re.sub(r'\W', '', words[i])))
    size = 40; font(ctx, 'sub', size, True)
    widths = [ctx.text_extents(w.translate(TR) + ' ').x_advance for w in words]
    x = W / 2 - sum(widths) / 2; y = H - 70
    g = cairo.LinearGradient(0, H - 220, 0, H); g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.65)
    ctx.rectangle(0, H - 220, W, 220); ctx.set_source(g); ctx.fill()
    for i, w in enumerate(words):
        txt(ctx, w, x, y, size, f='sub', col=AMB if i == lng else WHITE, align='l', bold=True)
        x += widths[i]

def shot_frame(ctx, s, t):
    KINDS[s['kind']](ctx, t - s['t0'], s['t1'] - s['t0'], s['p'])

def frame(t, surf):
    ctx = cairo.Context(surf)
    idx = next((i for i, s in enumerate(SHOTS) if s['t0'] <= t < s['t1']), len(SHOTS) - 1)
    s = SHOTS[idx]
    shot_frame(ctx, s, t)
    if idx > 0 and t - s['t0'] < XF:
        prev = SHOTS[idx - 1]
        tmp = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c2 = cairo.Context(tmp)
        shot_frame(c2, prev, min(t, prev['t1'] - 1e-3))
        ctx.set_source_surface(tmp, 0, 0); ctx.paint_with_alpha(1 - ease((t - s['t0']) / XF))
    grain(ctx, t)
    sb = sub_at(t)
    if sb: draw_sub(ctx, sb)
    if t < 0.5: ctx.rectangle(0, 0, W, H); src(ctx, (0, 0, 0), 1 - t / 0.5); ctx.fill()
    if t > TOTAL - 1.5: ctx.rectangle(0, 0, W, H); src(ctx, (0, 0, 0), clamp((t - (TOTAL - 1.5)) / 1.5)); ctx.fill()

def render_range(f0, f1, out):
    import subprocess
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    pr = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        frame(f / FPS, surf); surf.flush(); pr.stdin.write(bytes(surf.get_data()))
    pr.stdin.close(); pr.wait()

def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f'{h:02d}:{m:02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}'

if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'info':
        ds = [s['t1'] - s['t0'] for s in SHOTS]
        print('total', round(TOTAL, 1), 's', round(TOTAL / 60, 2), 'min', int(TOTAL * FPS), 'frames', len(SHOTS), 'shots, avg', round(sum(ds) / len(ds), 2), 'max', round(max(ds), 1))
    elif c == 'shots':
        surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); os.makedirs('stills', exist_ok=True); keys = set(sys.argv[2:])
        for j, s in enumerate(SHOTS):
            if keys and s['key'] not in keys: continue
            frame(s['t0'] + (s['t1'] - s['t0']) * 0.7, surf); surf.write_to_png(f'stills/sh_{j:03d}_{s["key"]}.png')
    elif c == 'range':
        render_range(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif c == 'srt':
        out = []
        for i, (a, b, s) in enumerate(SUBS): out += [str(i + 1), f'{ts(a)} --> {ts(b)}', s, '']
        open(sys.argv[2], 'w').write('\n'.join(out))
        for (key, kind, text), st in zip(LINES, STARTS):
            if kind == 'chapter':
                m, s = divmod(int(st), 60); print(f'{m:02d}:{s:02d} {text}')
    elif c == 'vo':
        print(json.dumps(dict(starts=STARTS, total=TOTAL)))
