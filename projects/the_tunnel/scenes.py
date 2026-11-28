"""3D hologram scenes for 'The Tunnel' (El Chapo, Altiplano 2015)."""
import sys, math
import numpy as np
import cairo
sys.path.insert(0, '/root/docengine')
from d3 import *

def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def lerp(a, b, k): return a + (b - a) * k
def seg(t, a, b): return max(0.0, min(1.0, (t - a) / (b - a))) if b > a else float(t >= a)
def u(t, d): return max(0.0, min(1.0, t / max(d, 0.1)))

def finish(ctx, t, cap=None, sub=None):
    s = ctx.get_target(); s.flush(); bloom(s, 0.85); s.mark_dirty()
    dust(ctx, t)
    scanlines(ctx, t)
    if cap:
        ctx.select_font_face('Bebas Neue'); ctx.set_font_size(58)
        w = ctx.text_extents(cap).x_advance
        a = min(1.0, t / 0.6)
        ctx.move_to(90, 150); ctx.set_source_rgba(1, 1, 1, 0.95 * a); ctx.show_text(cap)
        ctx.rectangle(90, 168, w * min(1, t / 0.9), 4); ctx.set_source_rgba(*RED, 0.9 * a); ctx.fill()
        if sub:
            ctx.select_font_face('PT Mono'); ctx.set_font_size(24)
            ctx.move_to(92, 212); ctx.set_source_rgba(0.7, 0.85, 1, 0.85 * a); ctx.show_text(sub)

def vary(p):
    v = p.get('v', 0)
    return (v * 1.7) % 6.283 if v else 0.0, 1.0 + ((v * 0.37) % 0.4) if v else 1.0

def orbit(t, d, tgt, r0, r1, a0, a1, h0, h1, fov=50):
    k = ease(u(t, d)); a = lerp(a0, a1, k); r = lerp(r0, r1, k)
    tgt = np.array(tgt, float)
    return Cam(tgt + np.array([r * math.cos(a), r * math.sin(a), lerp(h0, h1, k)]), tgt, fov)

# ------------------------------------------------------------------ models
def prison_model(cell_hl=True):
    ms, ln = [], []
    for (x, y, w, dd) in ((-60, -40, 160, 2), (-60, 38, 160, 2), (-60, -40, 2, 80), (98, -40, 2, 80)):
        ms.append(box(x, y, 0, w, dd, 7, alpha=0.10))
    for x, y in ((-62, -42), (98, -42), (-62, 38), (98, 38)):
        ms.append(box(x, y, 0, 4, 4, 16, alpha=0.18))
    for i in range(4):
        for yy in (-25, 8):
            b = building(-40 + i * 32, yy, 24, 18, 9, floors=3)
            ms.append(b[0]); ln.append(b[1])
    return ms, ln

CELL = (52, -23)
def cell_model():
    x, y = CELL
    return [box(x, y, 0, 4, 3, 3, col=RED, alpha=0.30)], [box(x + 0.3, y + 0.3, 0, 2.0, 0.9, 0.5, col=RED, alpha=0.4), box(x + 3.0, y, 0, 1.0, 1.0, 0.15, col=AMBER, alpha=0.6)]

L = 600.0
TP = [(55.5 + L * i / 40, -22.5 + 6 * math.sin(i / 7), -10) for i in range(41)]

def tunnel_model():
    t = tube(TP, r=1.0, seg=8, col=RED, alpha=0.12, edge=0.7)
    rails = Lines([((TP[i][0], TP[i][1] + o, -10.85), (TP[i + 1][0], TP[i + 1][1] + o, -10.85)) for i in range(40) for o in (-0.35, 0.35)], col=AMBER, edge=0.7)
    rings = Lines(sum([ring(np.array(TP[i]), 1.0, 'x', 14) for i in range(0, 41, 4)], []), col=RED, edge=0.5)
    shaft = tube([(55.5, -22.5, 0), (55.5, -22.5, -10)], r=0.6, col=RED, alpha=0.3)
    ex = (TP[-1][0], TP[-1][1])
    hsh = tube([(ex[0], ex[1], -10), (ex[0], ex[1], 0)], r=0.6, col=AMBER, alpha=0.3)
    house = box(ex[0] - 6, ex[1] - 4.5, 0, 12, 9, 5, col=AMBER, alpha=0.25)
    return [t, shaft, hsh, house], [rails, rings]

def bike(uu):
    i = min(39.999, uu * 40); j = int(i); fr = i - j
    p = np.array(TP[j]) * (1 - fr) + np.array(TP[j + 1]) * fr
    body = box(p[0] - 0.9, p[1] - 0.2, p[2] - 0.45, 1.8, 0.4, 0.5, col=AMBER, alpha=0.7)
    rider = box(p[0] - 0.2, p[1] - 0.2, p[2] + 0.05, 0.4, 0.4, 0.8, col=AMBER, alpha=0.5)
    wh = Lines(ring(p + np.array([-0.8, 0, -0.55]), 0.3, 'y', 10) + ring(p + np.array([0.8, 0, -0.55]), 0.3, 'y', 10), col=AMBER, edge=1.0, glow=True)
    return [body, rider], [wh]

def lamps(ctx, cam):
    pts = np.array([(p[0], p[1], -9.2) for p in TP])
    s_, d_ = cam.proj(pts)
    for (x, y), dd in zip(s_, d_):
        if dd > 0.1:
            ctx.arc(x, y, max(1.2, 60 / dd), 0, 2 * math.pi); ctx.set_source_rgba(1, 0.85, 0.5, 0.9); ctx.fill()

# ------------------------------------------------------------------ scenes
def s_prison(ctx, t, d, p):
    """Altiplano overview orbit; p: cap, sub, hl(cell)"""
    background(ctx)
    da, sc = vary(p)
    cam = orbit(t, d, (20, 0, 0), p.get('r0', 190) * sc, p.get('r1', 150) * sc, p.get('a0', -2.5) + da, p.get('a1', -1.9) + da, 120 * sc, 95 * sc)
    ground_grid(ctx, cam, size=400, step=10, a=0.14)
    ms, ln = prison_model()
    k = ease(seg(t, 0, 1.2))
    ms = [m.moved(sz=max(0.02, k)) for m in ms]
    if p.get('hl'):
        c, extra = cell_model(); c[0].edge = 0.6 + 0.4 * math.sin(t * 4); ms += c
        label3d(ctx, cam, (54, -21.5, 3), p.get('hl'), col=RED, size=44, a=seg(t, 1.2, 1.8))
    render(ctx, cam, ms); render_lines(ctx, cam, ln if k > 0.9 else [])
    for x, y in ((-60, -42), (100, -42), (-60, 40), (100, 40)):
        if p.get('towers'):
            label3d(ctx, cam, (x, y, 16), '', a=0)
    finish(ctx, t, p.get('cap'), p.get('sub'))

def s_escape(ctx, t, d, p):
    """Cell -> shower -> shaft -> tunnel -> house. p: phase 'dive' or 'ride'"""
    background(ctx)
    ms, ln = prison_model(); c, extra = cell_model(); tm, tl = tunnel_model()
    if p.get('phase') == 'dive':
        k = ease(u(t, d))
        cam = Cam(np.array([lerp(20, 50, k), lerp(-70, -32, k), lerp(55, -6, k)]), np.array([55.5, -22.5, lerp(0, -10, k)]), 55)
        ground_grid(ctx, cam, size=400, step=10, a=0.14)
        render(ctx, cam, ms + c + extra + tm[1:2]); render_lines(ctx, cam, ln)
        label3d(ctx, cam, (57, -22.5, -10), '~10 M DOWN', col=RED, size=52, a=seg(t, d * 0.6, d * 0.8))
    else:
        k = ease(u(t, d)); x = 55.5 + L * lerp(0.02, 0.93, k)
        cam = Cam(np.array([x - 30, -40, 2]), np.array([x + 25, -22, -10]), 55)
        ground_grid(ctx, cam, size=500, step=10, cx=300, a=0.14)
        bm, bl = bike(k)
        render(ctx, cam, ms + tm + bm); render_lines(ctx, cam, tl + bl); lamps(ctx, cam)
        label3d(ctx, cam, (TP[-1][0], TP[-1][1] + 6, 6), 'EXIT: HALF-BUILT HOUSE', col=AMBER, size=52, a=seg(t, 1.0, 1.6))
    finish(ctx, t, p.get('cap'), p.get('sub'))

def s_cell(ctx, t, d, p):
    """Cell interior with CCTV cone and blind spot behind shower wall."""
    background(ctx)
    da, sc = vary(p); da *= 0.25
    cam = orbit(t, d, (2, 1.5, 1.0), 9 * sc, 7.5 * sc, -2.2 + da, -1.6 + da, 6, 4.5, fov=55)
    ground_grid(ctx, cam, size=20, step=1, a=0.10, cx=2, cy=1.5)
    walls = [box(0, 0, 0, 4, 0.1, 3, alpha=0.08), box(0, 0, 0, 0.1, 3, 3, alpha=0.08), box(0, 2.9, 0, 4, 0.1, 3, alpha=0.08)]
    bed = box(0.2, 0.2, 0, 2.0, 0.9, 0.5, alpha=0.3)
    wall = box(3.0, 1.0, 0, 0.12, 2.0, 1.0, col=CYAN, alpha=0.35)   # low shower partition
    shower = box(3.1, 0.1, 0, 0.85, 0.85, 0.08, col=RED, alpha=0.7)
    ms = walls + [bed, wall, shower]
    render(ctx, cam, ms)
    # camera + cone
    camp = np.array([0.2, 2.8, 2.8])
    cone_t = [np.array(v) for v in ((2.6, 0.1, 0), (2.6, 2.9, 0), (0.1, 2.9, 0), (0.1, 0.1, 0))]
    a = seg(t, 0.8, 1.5)
    s_, d_ = cam.proj(np.array([camp] + cone_t))
    for q in s_[1:]:
        ctx.move_to(*s_[0]); ctx.line_to(*q); ctx.set_source_rgba(0.55, 0.85, 1, 0.35 * a); ctx.set_line_width(1.5); ctx.stroke()
    ctx.move_to(*s_[1])
    for q in s_[2:]: ctx.line_to(*q)
    ctx.close_path(); ctx.set_source_rgba(0.55, 0.85, 1, 0.10 * a); ctx.fill()
    label3d(ctx, cam, tuple(camp), 'CCTV', col=CYAN, size=38, a=a)
    b = seg(t, 2.0, 2.6)
    label3d(ctx, cam, (3.5, 0.5, 0.1), p.get('blind', 'BLIND SPOT'), col=RED, size=44, a=b)
    if b > 0:
        sp = cam.proj(np.array([(3.5, 0.5, 0.05)]))[0][0]
        ctx.arc(*sp, 30 + 10 * math.sin(t * 5), 0, 2 * math.pi); ctx.set_source_rgba(*RED, 0.7 * b); ctx.set_line_width(3); ctx.stroke()
    finish(ctx, t, p.get('cap'), p.get('sub'))

def s_section(ctx, t, d, p):
    """Tunnel cross-section with person for scale; p: h, w labels"""
    background(ctx)
    k0 = ease(u(t, d))
    cam = Cam(np.array([lerp(-5.5, -4.0, k0), lerp(-2.6, -2.0, k0), 1.5]), np.array([5, 0.3, 0.8]), 55)
    ground_grid(ctx, cam, size=12, step=1, a=0.10, z=0)
    hh, ww = p.get('h', 1.7), p.get('w', 0.8)
    segs_ = []
    for x in np.arange(-6, 8, 1.0):
        segs_ += [((x, -ww / 2, 0), (x, -ww / 2, hh)), ((x, ww / 2, 0), (x, ww / 2, hh)), ((x, -ww / 2, hh), (x, ww / 2, hh)), ((x, -ww / 2, 0), (x, ww / 2, 0))]
    segs_ += [((-6, -ww / 2, hh), (8, -ww / 2, hh)), ((-6, ww / 2, hh), (8, ww / 2, hh)), ((-6, -ww / 2, 0), (8, -ww / 2, 0)), ((-6, ww / 2, 0), (8, ww / 2, 0))]
    tun = Lines(segs_, col=RED, edge=0.7, glow=True)
    rails = Lines([((-6, o, 0.05), (8, o, 0.05)) for o in (-0.22, 0.22)], col=AMBER, edge=0.9)
    pipe = tube([(-6, ww / 2 - 0.08, hh - 0.12), (8, ww / 2 - 0.08, hh - 0.12)], r=0.06, seg=6, col=CYAN, alpha=0.3)
    man = person(1.0, 0, 0, h=1.7, col=CYAN, alpha=0.35)
    render(ctx, cam, [pipe] + man); render_lines(ctx, cam, [tun, rails])
    label3d(ctx, cam, (2.0, -ww / 2, hh), p.get('hl', '~1.7 M HIGH'), col=RED, size=52, a=seg(t, 0.8, 1.4))
    label3d(ctx, cam, (-2.0, ww / 2, 0.0), p.get('wl', '~0.8 M WIDE'), col=RED, size=52, a=seg(t, 1.4, 2.0), dy=14)
    label3d(ctx, cam, (4.0, ww / 2 - 0.08, hh - 0.12), 'VENTILATION', col=CYAN, size=36, a=seg(t, 2.0, 2.6))
    finish(ctx, t, p.get('cap'), p.get('sub'))

def s_topdown(ctx, t, d, p):
    """Prison -> house distance, top-down-ish"""
    background(ctx)
    k = ease(u(t, d))
    cam = Cam(np.array([lerp(280, 300, k), lerp(-560, -500, k), lerp(820, 760, k)]), np.array([300, 0, 0]), 58)
    ground_grid(ctx, cam, size=500, step=20, cx=300, a=0.14)
    ms, ln = prison_model(); tm, tl = tunnel_model()
    grow = seg(t, 0.8, d * 0.8)
    n = max(2, int(41 * grow))
    path = Lines([((TP[i][0], TP[i][1], 0.5), (TP[i + 1][0], TP[i + 1][1], 0.5)) for i in range(n - 1)], col=RED, edge=1.0, glow=True, width=6)
    hmark = box(TP[-1][0] - 10, TP[-1][1] - 8, 0, 20, 16, 8, col=AMBER, alpha=0.35)
    render(ctx, cam, ms + [hmark]); render_lines(ctx, cam, ln + [path])
    label3d(ctx, cam, (TP[-1][0], TP[-1][1] + 8, 6), p.get('house', 'HOUSE'), col=AMBER, size=42, a=seg(t, 1.0, 1.5))
    mid = TP[20]
    label3d(ctx, cam, (mid[0], mid[1] - 10, 0), p.get('dist', '~1.5 KM'), col=RED, size=52, a=seg(t, d * 0.6, d * 0.75), dy=14)
    finish(ctx, t, p.get('cap'), p.get('sub'))

def s_cart(ctx, t, d, p):
    """2001: laundry cart rolling out through gates (reported version)."""
    background(ctx)
    k0 = ease(u(t, d)); xc = lerp(-16, 34, k0)
    cam = Cam(np.array([xc - 22, -26, 12]), np.array([xc + 4, 0, 1]), 50)
    ground_grid(ctx, cam, size=80, step=4, a=0.12)
    gates = [box(x, -6, 0, 1.0, 12, 5, alpha=0.16) for x in (0, 12, 24)]
    walls = [box(-20, -8, 0, 60, 1, 6, alpha=0.08), box(-20, 7, 0, 60, 1, 6, alpha=0.08)]
    k = ease(u(t, d)); x = lerp(-16, 34, k)
    cart = box(x - 1, -0.7, 0.3, 2.0, 1.4, 1.2, col=RED, alpha=0.5)
    wheels = Lines(ring(np.array([x - 0.7, -0.7, 0.25]), 0.22, 'y', 8) + ring(np.array([x + 0.7, -0.7, 0.25]), 0.22, 'y', 8), col=RED, edge=1.0)
    render(ctx, cam, walls + gates + [cart]); render_lines(ctx, cam, [wheels])
    label3d(ctx, cam, (x, 0, 2), p.get('lab', 'LAUNDRY CART (REPORTED)'), col=RED, size=52, a=seg(t, 0.6, 1.2))
    finish(ctx, t, p.get('cap'), p.get('sub'))

def s_adx(ctx, t, d, p):
    """ADX cell 7x12 ft with slit window."""
    background(ctx)
    da, sc = vary(p); da *= 0.3
    cam = orbit(t, d, (1.1, 1.8, 1.0), 7.5 * sc, 6.0 * sc, -2.4 + da, -1.7 + da, 5, 3.5, fov=55)
    ground_grid(ctx, cam, size=10, step=1, a=0.10, cx=1, cy=2)
    w, dd, h = 2.13, 3.66, 2.6
    walls = [box(0, 0, 0, w, 0.08, h, alpha=0.08), box(0, 0, 0, 0.08, dd, h, alpha=0.08), box(w - 0.08, 0, 0, 0.08, dd, h, alpha=0.08), box(0, dd - 0.08, 0, w, 0.08, h, alpha=0.08)]
    bed = box(0.1, 0.1, 0, 0.8, 2.0, 0.45, col=CYAN, alpha=0.35)
    desk = box(w - 0.6, 2.4, 0.6, 0.5, 1.0, 0.08, col=CYAN, alpha=0.35)
    win = box(0.9, dd - 0.1, 1.0, 0.1, 0.12, 1.1, col=AMBER, alpha=0.8)
    render(ctx, cam, walls + [bed, desk, win])
    label3d(ctx, cam, (w / 2, 0, h), p.get('lab', '7 × 12 FEET'), col=RED, size=44, a=seg(t, 0.6, 1.2))
    label3d(ctx, cam, (0.95, dd - 0.1, 2.1), '4-INCH WINDOW', col=AMBER, size=36, a=seg(t, 1.4, 2.0))
    finish(ctx, t, p.get('cap'), p.get('sub'))

def s_house(ctx, t, d, p):
    """Generic building target (condo / safehouse) with arrows of forces converging."""
    background(ctx)
    da, sc = vary(p)
    cam = orbit(t, d, (0, 0, 4), 70 * sc, 50 * sc, -2.3 + da * 0.3, -1.6 + da * 0.3, 40, 26)
    ground_grid(ctx, cam, size=80, step=4, a=0.12)
    floors = p.get('floors', 2)
    b = building(-8, -6, 16, 12, 3.2 * floors, floors=floors, col=AMBER, alpha=0.18)
    ms = [b[0]]; ln = [b[1]]
    for gx in (-30, 30):
        for gy in (-28, 0, 28):
            ms.append(box(gx - 7, gy - 6, 0, 14, 12, 4 + (abs(gx + gy) % 3) * 2, alpha=0.06))
    ln.append(Lines([((-60, y, 0.05), (60, y, 0.05)) for y in (-14, 14)] + [((x, -60, 0.05), (x, 60, 0.05)) for x in (-18, 18)], col=AMBER, edge=0.35))
    k = seg(t, 0.6, d * 0.7)
    arrows = []
    for ang in (0.3, 1.6, 2.9, 4.2):
        r0, r1 = 45, 14
        r = lerp(r0, r1, ease(k))
        p0 = np.array([r0 * math.cos(ang), r0 * math.sin(ang), 0.3]); p1 = np.array([r * math.cos(ang), r * math.sin(ang), 0.3])
        arrows.append((p0, p1))
    render(ctx, cam, ms); render_lines(ctx, cam, ln + [Lines(arrows, col=RED, edge=1.0, glow=True, width=3)])
    if p.get('sewer'):
        sw = tube([(0, 0, -3), (40, 10, -3)], r=0.7, seg=8, col=RED, alpha=0.15)
        render(ctx, cam, [sw]); label3d(ctx, cam, (30, 7.5, -3), 'STORM DRAIN', col=RED, size=38, a=seg(t, 1.5, 2.1), dy=14)
    label3d(ctx, cam, (0, 0, 3.2 * floors), p.get('lab', ''), col=AMBER, size=42, a=seg(t, 0.4, 1.0))
    finish(ctx, t, p.get('cap'), p.get('sub'))


def s_condo(ctx, t, d, p):
    """Seafront condominium tower, highlighted floor, marines converging."""
    background(ctx)
    da, sc = vary(p)
    cam = orbit(t, d, (0, 0, 10), 95 * sc, 70 * sc, -2.0 + da * 0.3, -1.3 + da * 0.3, 40, 28)
    ground_grid(ctx, cam, size=120, step=5, a=0.12)
    sea = Lines([((-120, y, 0), (120, y, 0)) for y in range(18, 120, 4)], col=CYAN, edge=0.25)
    road = Lines([((-120, 10, 0.05), (120, 10, 0.05)), ((-120, 15, 0.05), (120, 15, 0.05))], col=AMBER, edge=0.5)
    tw = building(-7, -6, 14, 10, 30, floors=10, col=BLUE, alpha=0.12, win=5)
    fl = box(-7.2, -6.2, 9.0, 14.4, 10.4, 3.0, col=RED, alpha=0.35)
    fl.edge = 0.6 + 0.4 * math.sin(t * 4)
    nb = [building(x, -8, 10, 12, h, floors=f, alpha=0.08, win=3)[0] for x, h, f in ((-30, 18, 6), (16, 22, 7), (32, 12, 4), (-46, 14, 5))]
    k = seg(t, 0.8, d * 0.8); arr = []
    for ang in (2.2, 3.1, 4.0, 4.9):
        r = lerp(70, 16, ease(k)); arr.append((np.array([70 * math.cos(ang), 70 * math.sin(ang) - 20, 0.3]), np.array([r * math.cos(ang), r * math.sin(ang) - 20, 0.3])))
    render(ctx, cam, nb + [tw[0], fl]); render_lines(ctx, cam, [sea, road, tw[1], Lines(arr, col=RED, edge=1.0, glow=True, width=3)])
    label3d(ctx, cam, (0, -6, 12), p.get('lab', '4TH FLOOR'), col=RED, size=44, a=seg(t, 0.5, 1.1))
    label3d(ctx, cam, (40, 40, 0), 'PACIFIC OCEAN', col=CYAN, size=34, a=seg(t, 0.3, 0.9) * 0.8, dy=0)
    finish(ctx, t, p.get('cap'), p.get('sub'))

def s_chase(ctx, t, d, p):
    """Highway: stolen car stopped by police cars."""
    background(ctx)
    da, sc = vary(p)
    k = ease(u(t, d)); x = lerp(-60, 18, min(1, k * 1.3))
    cam = Cam(np.array([x - 16 + da, -17 * sc, 8]), np.array([x + 8, 0, 0.5]), 50)
    ground_grid(ctx, cam, size=160, step=8, a=0.10, cx=x)
    road = Lines([((-200, o, 0.05), (200, o, 0.05)) for o in (-5, 5)] + [((xx, 0, 0.05), (xx + 4, 0, 0.05)) for xx in range(-200, 200, 10)], col=AMBER, edge=0.6)
    car = box(x - 2.2, -3.6, 0.3, 4.4, 2.0, 1.4, col=RED, alpha=0.5)
    cops = [box(26 + i * 0.5, -4.5 + i * 3.2, 0.3, 4.4, 2.0, 1.4, col=CYAN, alpha=0.45).moved() for i in range(3)]
    render(ctx, cam, cops + [car]); render_lines(ctx, cam, [road])
    if k > 0.6:
        for i, c in enumerate(cops):
            s_, d_ = cam.proj(np.array([(28 + i * 0.5, -3.5 + i * 3.2, 2.2)]))
            on = (int(t * 6) + i) % 2
            ctx.arc(*s_[0], 9, 0, 2 * math.pi); ctx.set_source_rgba(*(RED if on else BLUE), 0.9); ctx.fill()
    label3d(ctx, cam, (x, -2.6, 1.8), p.get('lab', 'STOLEN CAR'), col=RED, size=40, a=seg(t, 0.4, 1.0))
    label3d(ctx, cam, (28, 4, 1.8), 'FEDERAL POLICE', col=CYAN, size=40, a=seg(t, d * 0.55, d * 0.7))
    finish(ctx, t, p.get('cap'), p.get('sub'))

def s_court(ctx, t, d, p):
    """Courtroom schematic: bench, witness stand, jury box, defense table."""
    background(ctx)
    da, sc = vary(p); da *= 0.4
    cam = orbit(t, d, (0, 4, 1.5), 22 * sc, 17 * sc, -1.9 + da, -1.3 + da, 9, 7)
    ground_grid(ctx, cam, size=30, step=1, a=0.08, cy=4)
    bench = box(-3, 10, 0, 6, 1.6, 1.6, alpha=0.3)
    judge = person(0, 11.2, 1.0, h=1.0, col=CYAN, alpha=0.35)
    jury = [box(7, 3 + r * 1.2, r * 0.3, 4.5, 1.0, 0.9, alpha=0.2) for r in range(2)]
    jurors = sum([person(7.6 + i * 1.1, 3.5 + r * 1.2, r * 0.3 + 0.4, h=1.0, col=CYAN, alpha=0.3) for r in range(2) for i in range(4)], [])
    defense = box(-5, 3, 0, 4, 1.4, 0.8, col=RED, alpha=0.35)
    accused = person(-3, 2.4, 0, h=1.7, col=RED, alpha=0.4)
    rows = [box(-8, -4 - r * 1.6, 0, 16, 0.6, 0.9, alpha=0.08) for r in range(4)]
    render(ctx, cam, rows + [bench, defense] + jury + judge + jurors + accused)
    label3d(ctx, cam, (8.5, 4, 2.2), 'JURY', col=CYAN, size=40, a=seg(t, 0.6, 1.2))
    label3d(ctx, cam, (-3, 2.4, 1.8), p.get('lab', 'THE DEFENDANT'), col=RED, size=40, a=seg(t, 1.0, 1.6))
    finish(ctx, t, p.get('cap'), p.get('sub'))

def s_border(ctx, t, d, p):
    """House in Mexico -> tunnel under the border fence -> warehouse in the US."""
    background(ctx)
    da, sc = vary(p)
    k = ease(u(t, d))
    cam = Cam(np.array([lerp(-30, 10, k) + da, -115 * sc, 55]), np.array([lerp(0, 15, k), 0, -4]), 50)
    ground_grid(ctx, cam, size=120, step=6, a=0.12)
    fence = Lines([((0, y, 0), (0, y, 5)) for y in range(-60, 61, 3)] + [((0, -60, 5), (0, 60, 5)), ((0, -60, 2.5), (0, 60, 2.5))], col=AMBER, edge=0.6)
    house = box(-40, -6, 0, 12, 10, 5, col=RED, alpha=0.25)
    ware = box(40, -9, 0, 20, 16, 8, col=CYAN, alpha=0.2)
    n = max(2, int(30 * seg(t, 0.6, d * 0.75)))
    path = [(-34 + 80 * i / 29, -1 + 2 * math.sin(i / 5), -8) for i in range(30)]
    tun = tube([(-34, -1, 0)] + path[:n], r=0.9, seg=8, col=RED, alpha=0.15, edge=0.8)
    render(ctx, cam, [house, ware, tun]); render_lines(ctx, cam, [fence])
    label3d(ctx, cam, (-34, -1, 5), p.get('la', 'MEXICO'), col=RED, size=40, a=seg(t, 0.3, 0.9))
    label3d(ctx, cam, (50, -1, 8), p.get('lb', 'UNITED STATES'), col=CYAN, size=40, a=seg(t, 0.5, 1.1))
    label3d(ctx, cam, (0, 40, 5), 'BORDER', col=AMBER, size=36, a=seg(t, 0.2, 0.8))
    finish(ctx, t, p.get('cap'), p.get('sub'))
