"""Mini 3D hologram renderer (cairo): flat-shaded meshes + glowing edges, perspective camera.
Style: dark blueprint background, cyan/blue structures, red highlights."""
import math
import numpy as np
import cairo

W, H = 1920, 1080
BLUE = (0.33, 0.66, 1.0)
CYAN = (0.55, 0.85, 1.0)
RED = (1.0, 0.22, 0.18)
AMBER = (1.0, 0.72, 0.30)


def v3(*a): return np.array(a, dtype=float)


class Mesh:
    def __init__(self, verts, faces, col=BLUE, alpha=0.22, edge=0.9, glow=True, name=''):
        self.v = np.array(verts, float); self.f = faces; self.col = col; self.alpha = alpha
        self.edge = edge; self.glow = glow; self.name = name
        self.edges = set()
        for f in faces:
            for i in range(len(f)):
                a, b = f[i], f[(i + 1) % len(f)]
                self.edges.add((min(a, b), max(a, b)))
        self.edges = sorted(self.edges)

    def moved(self, off=(0, 0, 0), sz=1.0, sx=1.0, rot=0.0):
        v = self.v.copy()
        if rot:
            c, s = math.cos(rot), math.sin(rot)
            v = v @ np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]]).T
        v = v * np.array([sx, sx, sz]) + np.array(off)
        m = Mesh.__new__(Mesh); m.__dict__ = dict(self.__dict__); m.v = v; return m


def box(x, y, z, w, d, h, **k):
    v = [(x, y, z), (x + w, y, z), (x + w, y + d, z), (x, y + d, z),
         (x, y, z + h), (x + w, y, z + h), (x + w, y + d, z + h), (x, y + d, z + h)]
    f = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return Mesh(v, f, **k)


def tube(path, r=1.0, seg=8, **k):
    """Tube along polyline path (list of xyz)."""
    path = [np.array(p, float) for p in path]
    verts, faces = [], []
    for i, p in enumerate(path):
        t = (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]); t /= (np.linalg.norm(t) + 1e-9)
        up = np.array([0, 0, 1.0]) if abs(t[2]) < 0.9 else np.array([1.0, 0, 0])
        n1 = np.cross(t, up); n1 /= np.linalg.norm(n1); n2 = np.cross(t, n1)
        for j in range(seg):
            a = 2 * math.pi * j / seg
            verts.append(p + r * (math.cos(a) * n1 + math.sin(a) * n2))
    for i in range(len(path) - 1):
        for j in range(seg):
            a = i * seg + j; b = i * seg + (j + 1) % seg
            faces.append((a, b, b + seg, a + seg))
    return Mesh(verts, faces, **k)


def person(x, y, z, h=1.8, **k):
    m1 = box(x - 0.22, y - 0.15, z, 0.44, 0.3, h * 0.78, **k)
    m2 = box(x - 0.14, y - 0.14, z + h * 0.8, 0.28, 0.28, h * 0.2, **k)
    return [m1, m2]


class Cam:
    def __init__(self, pos, look, fov=50):
        self.pos = np.array(pos, float); look = np.array(look, float)
        f = look - self.pos; self.f = f / np.linalg.norm(f)
        up = np.array([0, 0, 1.0])
        self.r = np.cross(self.f, up); self.r /= np.linalg.norm(self.r)
        self.u = np.cross(self.r, self.f)
        self.k = (W / 2) / math.tan(math.radians(fov) / 2)

    def proj(self, P):
        d = P - self.pos
        x = d @ self.r; y = d @ self.u; z = d @ self.f
        z = np.maximum(z, 0.05)
        return np.stack([W / 2 + self.k * x / z, H / 2 - self.k * y / z], -1), z


LIGHT = v3(-0.4, -0.6, 0.7); LIGHT /= np.linalg.norm(LIGHT)


def background(ctx, t=0.0):
    g = cairo.RadialGradient(W / 2, H * 0.45, 100, W / 2, H * 0.5, W * 0.8)
    g.add_color_stop_rgb(0, 0.055, 0.075, 0.11); g.add_color_stop_rgb(1, 0.012, 0.015, 0.025)
    ctx.set_source(g); ctx.paint()


def ground_grid(ctx, cam, size=200, step=10, z=0.0, col=BLUE, a=0.18, cx=0, cy=0):
    for i in range(-size, size + 1, step):
        for (p0, p1) in (((cx + i, cy - size, z), (cx + i, cy + size, z)), ((cx - size, cy + i, z), (cx + size, cy + i, z))):
            P = np.linspace(np.array(p0, float), np.array(p1, float), 24)
            s, d = cam.proj(P)
            for j in range(len(P) - 1):
                if d[j] <= 0.2 or d[j + 1] <= 0.2: continue
                fade = a * max(0.0, 1 - min(d[j], d[j + 1]) / (size * 1.3))
                if fade <= 0.003: continue
                ctx.move_to(*s[j]); ctx.line_to(*s[j + 1])
                ctx.set_source_rgba(*col, fade); ctx.set_line_width(1.2); ctx.stroke()


def render(ctx, cam, meshes, build=1.0, edge_k=1.0):
    """Painter's algorithm over all faces; then glowing edges."""
    faces = []
    for m in meshes:
        s, d = cam.proj(m.v)
        if np.all(d <= 0.06): continue
        for f in m.f:
            pts = m.v[list(f)]
            n = np.cross(pts[1] - pts[0], pts[2] - pts[0]); nn = np.linalg.norm(n)
            if nn < 1e-9: continue
            n /= nn
            depth = float(np.mean(d[list(f)]))
            if np.any(d[list(f)] <= 0.06): continue
            shade = 0.45 + 0.55 * abs(float(n @ LIGHT))
            faces.append((depth, s[list(f)], m, shade))
    faces.sort(key=lambda x: -x[0])
    for depth, pts, m, shade in faces:
        ctx.move_to(*pts[0])
        for p in pts[1:]: ctx.line_to(*p)
        ctx.close_path()
        ctx.set_source_rgba(m.col[0] * shade, m.col[1] * shade, m.col[2] * shade, m.alpha)
        ctx.fill()
    # edges with glow
    for m in meshes:
        s, d = cam.proj(m.v)
        for (a, b) in m.edges:
            if d[a] <= 0.06 or d[b] <= 0.06: continue
            fade = max(0.35, 1 - 0.5 * min(d[a], d[b]) / 1500)
            pa, pb = s[a], s[b]
            if m.glow:
                for w, al in ((9, 0.05), (5, 0.10)):
                    ctx.move_to(*pa); ctx.line_to(*pb); ctx.set_source_rgba(*m.col, al * m.edge * edge_k * fade); ctx.set_line_width(w); ctx.stroke()
            ctx.move_to(*pa); ctx.line_to(*pb)
            ctx.set_source_rgba(min(1, m.col[0] + 0.25), min(1, m.col[1] + 0.25), min(1, m.col[2] + 0.25), 0.95 * m.edge * edge_k * fade)
            ctx.set_line_width(1.6); ctx.stroke()


def label3d(ctx, cam, P, text, col=CYAN, size=30, a=1.0, font='Bebas Neue', dy=-14):
    s, d = cam.proj(np.array([P], float))
    if d[0] <= 0.1 or a <= 0: return
    x, y = s[0]
    ctx.select_font_face(font); ctx.set_font_size(size)
    w = ctx.text_extents(text).x_advance
    ctx.move_to(x, y); ctx.line_to(x, y + dy * 3); ctx.set_source_rgba(*col, 0.7 * a); ctx.set_line_width(1.5); ctx.stroke()
    ctx.move_to(x - w / 2, y + dy * 3 - 8); ctx.set_source_rgba(*col, a); ctx.show_text(text)


def scanlines(ctx, t):
    ctx.set_source_rgba(0.6, 0.8, 1.0, 0.025)
    for y in range(0, H, 4):
        ctx.rectangle(0, y, W, 1)
    ctx.fill()
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.4, W / 2, H / 2, H * 1.05)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.7)
    ctx.set_source(g); ctx.paint()


class Lines:
    """Edge-only object: list of (p0, p1) segments."""
    def __init__(self, segs, col=BLUE, edge=0.6, glow=False, width=1.2):
        self.segs = [(np.array(a, float), np.array(b, float)) for a, b in segs]; self.col = col; self.edge = edge; self.glow = glow; self.width = width


def render_lines(ctx, cam, objs):
    for o in objs:
        for a, b in o.segs:
            s, d = cam.proj(np.array([a, b]))
            if d[0] <= 0.06 or d[1] <= 0.06: continue
            fade = max(0.35, 1 - 0.5 * min(d) / 1500)
            if o.glow:
                ctx.move_to(*s[0]); ctx.line_to(*s[1]); ctx.set_source_rgba(*o.col, 0.12 * o.edge * fade); ctx.set_line_width(6); ctx.stroke()
            ctx.move_to(*s[0]); ctx.line_to(*s[1]); ctx.set_source_rgba(*o.col, o.edge * fade); ctx.set_line_width(o.width); ctx.stroke()


def building(x, y, w, d, h, floors=3, col=BLUE, alpha=0.14, win=6):
    m = box(x, y, 0, w, d, h, col=col, alpha=alpha)
    segs = []
    for k in range(1, floors):
        z = h * k / floors
        segs += [((x, y, z), (x + w, y, z)), ((x, y + d, z), (x + w, y + d, z)), ((x, y, z), (x, y + d, z)), ((x + w, y, z), (x + w, y + d, z))]
    for i in range(1, win):
        xx = x + w * i / win
        for k in range(floors):
            z0 = h * k / floors + h / floors * 0.35; z1 = z0 + h / floors * 0.35
            segs += [((xx - 0.6, y - 0.01, z0), (xx + 0.6, y - 0.01, z0)), ((xx - 0.6, y - 0.01, z1), (xx + 0.6, y - 0.01, z1)),
                     ((xx - 0.6, y - 0.01, z0), (xx - 0.6, y - 0.01, z1)), ((xx + 0.6, y - 0.01, z0), (xx + 0.6, y - 0.01, z1))]
    return [m, Lines(segs, col=col, edge=0.35)]


def ring(c, r, axis='x', n=16):
    pts = []
    for j in range(n + 1):
        a = 2 * math.pi * j / n
        if axis == 'x': pts.append(c + np.array([0, r * math.cos(a), r * math.sin(a)]))
        else: pts.append(c + np.array([r * math.cos(a), 0, r * math.sin(a)]))
    return [(pts[j], pts[j + 1]) for j in range(n)]


def bloom(surf, strength=0.85):
    from PIL import Image, ImageFilter
    w, h = surf.get_width(), surf.get_height()
    buf = np.ndarray((h, w, 4), np.uint8, surf.get_data())
    small = Image.fromarray(buf[::4, ::4, :3].copy())
    small = small.filter(ImageFilter.GaussianBlur(6))
    big = np.asarray(small.resize((w, h), Image.BILINEAR)).astype(np.uint16)
    out = np.clip(buf[:, :, :3].astype(np.uint16) + (big * strength).astype(np.uint16) // 1, 0, 255).astype(np.uint8)
    buf[:, :, :3] = out


def dust(ctx, t, n=70, seed=5):
    rnd = np.random.default_rng(seed)
    xs = rnd.random(n) * W; ys = rnd.random(n) * H; sp = rnd.random(n) * 8 + 3; sz = rnd.random(n) * 1.6 + 0.6
    for i in range(n):
        x = (xs[i] + t * sp[i]) % W; y = (ys[i] - t * sp[i] * 0.4) % H
        ctx.arc(x, y, sz[i], 0, 2 * math.pi); ctx.set_source_rgba(0.6, 0.8, 1.0, 0.18); ctx.fill()
