"""backdrop.py - distant snow mountain: the whole mountain is visible (blurry) at
first, and gets bigger and sharper the higher you climb.

* progress u = height above ground / summit height (0..1);
* zoom: far away the whole mountain is 0.28 of the screen height, at the summit
  it is zoomed 4.2x (near = big);
* sharpness: far away the mountain is rendered into a tiny texture and scaled up
  (= blurry); the resolution rises to 1:1 as you climb;
* position: the far stage lives in screen space (with left/right parallax); near
  the summit it locks to world coordinates and the platform top lines up exactly
  with the summit height - that is why it "becomes a real platform" at that range;
* the summit platform and cabin both come from this backdrop, no extra GameObject.
"""

import random

import pygame


class Backdrop:
    FINAL_HEIGHT = 18000
    SUMMIT_X = 6000
    TOP = 18000

    ZOOM_FAR = 0.28        # initial mountain size (fraction of screen height)
    ZOOM_NEAR = 4.2        # zoom at the summit (platform width ~ 4400 @1920)
    BLUR_FAR = 0.20        # render resolution far away (smaller = blurrier)
    CLEAR_U = 0.772        # height 13900: from here it gets sharper
    ANCHOR_A = 0.85        # screen anchor -> world anchor blend start
    ANCHOR_B = 0.97        # fully locked to world coordinates
    PARALLAX = 0.18        # horizontal parallax
    SKY_Y = 0.18           # summit screen height while far away
    RISE = 0.10            # before 13900: no zoom, just rising
    R_STEPS = (0.20, 0.26, 0.34, 0.45, 0.58, 0.72, 0.86, 1.0)
    STRATA_U = 0.78        # draw strata only after entering the clear zone
    STREAK_U = 0.85        # draw slope grooves a bit closer
    PLAIN_U = 0.95         # near the top: body + snow + cabin only

    def __init__(self, width, height, sky, ground_level, final_height=None,
                 summit_x=None, summit_top=None):
        self.width, self.height = width, height
        self.sky = sky
        self.ground = ground_level
        self.final_height = float(final_height or self.FINAL_HEIGHT)
        self.summit_x = float(summit_x or self.SUMMIT_X)
        self.summit_top = float(summit_top or self.TOP)
        self.w = int(width * 1.60)
        self.h = int(height * 1.90)
        self._buffers = {}
        self._build_shapes()

    # ------------------------------------------------------------ shape
    def _build_shapes(self):
        w, h = self.w, self.h
        base_y = h - 12
        self.base_y = base_y

        self.peak_y = int(h * 0.075)
        # summit platform world width is fixed at 4400 (not resolution dependent)
        self.plateau_half = int(4400 / self.ZOOM_NEAR / 2)
        self.cx = w // 2
        self.main_pts, left_pts, right_pts = self._main_ridge(
            self.cx, self.peak_y, self.plateau_half, base_y, w * 0.34, steps=32)
        self.main_ext, _, _ = self._main_ridge(
            self.cx, self.peak_y, self.plateau_half, base_y, w * 0.34,
            steps=56, u_max=7.0)

        # Slope grooves
        self.streaks = []
        srng = random.Random(21)

        def half_at(u):
            return self.plateau_half + w * 0.34 * (u ** 0.55)

        for _ in range(20):
            side = srng.choice((-1, 1))
            u0 = srng.uniform(0.02, 0.30)
            u1 = min(0.99, u0 + srng.uniform(0.18, 0.34))
            x0 = self.cx + side * half_at(u0) * srng.uniform(0.10, 0.75)
            x1 = self.cx + side * half_at(u1) * srng.uniform(0.10, 0.75)
            y0 = self.peak_y + (base_y - self.peak_y) * u0
            y1 = self.peak_y + (base_y - self.peak_y) * u1
            self.streaks.append(((x0, y0), (x1, y1), srng.randint(2, 4)))

        # Horizontal strata
        self.strata = []
        span = base_y - self.peak_y
        for u in [0.02 + 0.035 * i for i in range(27)]:
            hwid = self.plateau_half + w * 0.34 * (u ** 0.55)
            y0 = self.peak_y + span * u
            self.strata.append((y0, y0 + span * 0.045, hwid))

        # Snow cap
        cap_y = self.peak_y + int((base_y - self.peak_y) * 0.06)
        cap_left = [p for p in left_pts if p[1] <= cap_y]
        cap_right = [p for p in right_pts if p[1] <= cap_y]
        self.snow = []
        if cap_left and cap_right:
            rng = random.Random(9)
            a, b = cap_left[-1], cap_right[-1]
            jag = [(a[0] + (b[0] - a[0]) * i / 7, cap_y + rng.uniform(-18, 10))
                   for i in range(1, 7)]
            self.snow = ([(self.cx - self.plateau_half, self.peak_y)] + cap_left + jag +
                         list(reversed(cap_right)) +
                         [(self.cx + self.plateau_half, self.peak_y)])

        # Summit cabin (platform offset right)
        bw = max(60, int(w * 0.035))
        bh = max(50, int(w * 0.026))
        roof_h = int(bh * 0.7)
        hx = self.cx + int(w * 0.040) - bw // 2
        self.house_img = (hx, self.peak_y - bh - roof_h, bw, bh + roof_h)

    @staticmethod
    def _ridge(cx, summit_y, base_y, half_w, steps=10):
        rng = random.Random(int(cx * 7 + summit_y * 3))
        pts = []
        for i in range(steps):
            t = i / steps
            pts.append((cx - half_w * (1 - t) + rng.uniform(-16, 16),
                        base_y + (summit_y - base_y) * (t ** 1.4) + rng.uniform(-12, 12)))
        pts.append((cx, summit_y))
        for i in range(steps - 1, -1, -1):
            t = i / steps
            pts.append((cx + half_w * (1 - t) + rng.uniform(-16, 16),
                        base_y + (summit_y - base_y) * (t ** 1.4) + rng.uniform(-12, 12)))
        pts += [(cx + half_w, base_y), (cx - half_w, base_y)]
        return pts

    @staticmethod
    def _main_ridge(cx, peak_y, plateau_half, base_y, half_w, steps=16, u_max=1.0):
        rng = random.Random(11)
        height = base_y - peak_y
        left, right = [], []
        for i in range(1, steps + 1):
            u = u_max * i / steps
            half = plateau_half + half_w * (u ** 0.55)
            y = peak_y + height * u + rng.uniform(-9, 9) * u
            left.append((cx - half + rng.uniform(-9, 9) * u, y))
            right.append((cx + half + rng.uniform(-9, 9) * u,
                          peak_y + height * u + rng.uniform(-9, 9) * u))
        pts = ([(cx - plateau_half, peak_y)] + left +
               list(reversed(right)) + [(cx + plateau_half, peak_y)])
        return pts, left, right

    @staticmethod
    def _clip_poly(pts, xmin, ymin, xmax, ymax):
        """Sutherland-Hodgman: clip polygons to the view to avoid huge fills."""
        def clip(points, inside, inter):
            out = []
            n = len(points)
            if n == 0:
                return out
            for i in range(n):
                cur, prv = points[i], points[i - 1]
                ci, pi = inside(cur), inside(prv)
                if ci:
                    if not pi:
                        out.append(inter(prv, cur))
                    out.append(cur)
                elif pi:
                    out.append(inter(prv, cur))
            return out

        def cross_x(a, b, x):
            t = (x - a[0]) / (b[0] - a[0]) if b[0] != a[0] else 0.0
            return (x, a[1] + (b[1] - a[1]) * t)

        def cross_y(a, b, y):
            t = (y - a[1]) / (b[1] - a[1]) if b[1] != a[1] else 0.0
            return (a[0] + (b[0] - a[0]) * t, y)

        pts = clip(pts, lambda p: p[0] >= xmin, lambda a, b: cross_x(a, b, xmin))
        pts = clip(pts, lambda p: p[0] <= xmax, lambda a, b: cross_x(a, b, xmax))
        pts = clip(pts, lambda p: p[1] >= ymin, lambda a, b: cross_y(a, b, ymin))
        pts = clip(pts, lambda p: p[1] <= ymax, lambda a, b: cross_y(a, b, ymax))
        return pts

    # ------------------------------------------------------------ transform
    @staticmethod
    def _smooth(x):
        x = max(0.0, min(1.0, x))
        return x * x * (3 - 2 * x)

    def _transform(self, camera_x, camera_y, feet):
        u = max(0.0, min(1.0, feet / self.summit_top))
        if u <= self.CLEAR_U:
            # Before 13900: no zoom, only rise with height
            zoom = self.ZOOM_FAR
            rise = self._smooth(u / self.CLEAR_U)
        else:
            # After 13900: start zooming in (near = big)
            t = (u - self.CLEAR_U) / (1.0 - self.CLEAR_U)
            zoom = self.ZOOM_FAR + (self.ZOOM_NEAR - self.ZOOM_FAR) * self._smooth(t)
            rise = 1.0
        f = self._smooth((u - self.ANCHOR_A) / (self.ANCHOR_B - self.ANCHOR_A))
        # World anchor: center of the summit top
        wx = self.summit_x - camera_x
        wy = (self.ground - self.summit_top) - camera_y
        # Screen anchor: whole mountain centered above, with parallax
        px = -(camera_x - self.summit_x) * self.PARALLAX * (0.10 + 0.90 * self._smooth(u))
        limit = self.width * 0.28
        px = max(-limit, min(limit, px))
        dx = self.width * 0.5 + px
        dy = self.height * (self.SKY_Y - self.RISE * rise)
        ax = dx + (wx - dx) * f
        ay = dy + (wy - dy) * f
        return ax, ay, zoom, f

    # ------------------------------------------------------------ draw
    def _draw_shapes(self, surface, ax, ay, zoom, scale, u):
        cxp, pk = self.cx, self.peak_y

        def sp(p):
            return (int((ax + (p[0] - cxp) * zoom) * scale),
                    int((ay + (p[1] - pk) * zoom) * scale))

        sw, sh = surface.get_size()
        box = (-4, -4, sw + 4, sh + 4)

        def draw_poly(color, points):
            clipped = self._clip_poly([sp(p) for p in points], *box)
            if len(clipped) >= 3:
                pygame.draw.polygon(surface, color, clipped)

        draw_poly((40, 44, 104), self.main_ext)
        body = (40, 44, 104)

        def clamp01(v):
            return max(0.0, min(1.0, v))

        def mix(c, t):
            return (int(body[0] + (c[0] - body[0]) * t),
                    int(body[1] + (c[1] - body[1]) * t),
                    int(body[2] + (c[2] - body[2]) * t))

        # Detail texture: none far away or very close, fades in between
        a_strata = (clamp01((u - self.STRATA_U) / 0.06) *
                    clamp01((self.PLAIN_U - u) / 0.08))
        a_streak = (clamp01((u - self.STREAK_U) / 0.06) *
                    clamp01((self.PLAIN_U - u) / 0.08))
        if a_strata > 0.02:
            for idx, (y0, y1, hwid) in enumerate(self.strata):
                base = (47, 51, 116) if idx % 2 == 0 else (35, 39, 96)
                pygame.draw.polygon(surface, mix(base, a_strata), [
                    sp((self.cx - hwid, y0)), sp((self.cx + hwid, y0)),
                    sp((self.cx + hwid, y1)), sp((self.cx - hwid, y1))])
        if a_streak > 0.02:
            for a, b, wd in self.streaks:
                pygame.draw.line(surface, mix((30, 34, 88), a_streak), sp(a), sp(b),
                                 max(1, int(wd * zoom * scale)))
        if self.snow:
            draw_poly((198, 208, 230), self.snow)
        self._draw_house(surface, ax, ay, zoom, scale)

    def _draw_house(self, surface, ax, ay, zoom, scale):
        cxp, pk = self.cx, self.peak_y
        hx, hy, hw, hh = self.house_img
        sx = (ax + (hx - cxp) * zoom) * scale
        sy = (ay + (hy - pk) * zoom) * scale
        w = hw * zoom * scale
        h = hh * zoom * scale
        if w < 2 or h < 2:
            return
        roof_h = h * 0.42
        body_h = h - roof_h
        pygame.draw.rect(surface, (84, 58, 46), (sx, sy + roof_h, w, body_h))
        pygame.draw.rect(surface, (58, 40, 34), (sx, sy + roof_h, w, max(1, h * 0.03)))
        pygame.draw.polygon(surface, (104, 68, 52),
                            [(sx - w * 0.10, sy + roof_h), (sx + w * 1.10, sy + roof_h),
                             (sx + w / 2, sy)])
        pygame.draw.polygon(surface, (222, 230, 242),
                            [(sx - w * 0.06, sy + roof_h - h * 0.03),
                             (sx + w * 1.06, sy + roof_h - h * 0.03),
                             (sx + w / 2, sy + h * 0.04)])
        dw, dh = w * 0.18, body_h * 0.62
        dx = sx + w / 2 - dw / 2
        pygame.draw.rect(surface, (40, 27, 24), (dx, sy + roof_h + body_h - dh, dw, dh))
        pygame.draw.circle(surface, (214, 180, 96),
                           (int(dx + dw * 0.82), int(sy + roof_h + body_h - dh / 2)),
                           max(1, int(w * 0.02)))
        win = w * 0.15
        for wx in (sx + w / 2 - dw - win - w * 0.22, sx + w / 2 + dw + w * 0.22):
            wy = sy + roof_h + body_h * 0.18
            pygame.draw.rect(surface, (255, 214, 130), (wx, wy, win, win))
            pygame.draw.rect(surface, (62, 42, 30), (wx, wy, win, win), max(1, int(w * 0.012)))
        chw, chh = w * 0.09, h * 0.26
        chx, chy = sx + w * 0.80, sy + roof_h - chh
        pygame.draw.rect(surface, (72, 52, 46), (chx, chy, chw, chh))
        for i, r in enumerate((0.040, 0.052, 0.066)):
            pygame.draw.circle(surface, (152, 158, 178),
                               (int(chx + chw / 2), int(chy - h * 0.05 - i * h * 0.10)),
                               max(1, int(w * r)))

    def _buffer(self, r):
        key = int(round(r * 1000))
        buf = self._buffers.get(key)
        if buf is None:
            bw, bh = max(2, int(self.width * r)), max(2, int(self.height * r))
            buf = pygame.Surface((bw, bh))
            self._buffers[key] = buf
        return buf

    def draw(self, screen, camera_x, camera_y, feet):
        ax, ay, zoom, f = self._transform(camera_x, camera_y, feet)
        u = max(0.0, min(1.0, feet / self.summit_top))
        sharp = self._smooth((u - self.CLEAR_U) / (1.0 - self.CLEAR_U))
        r = self.BLUR_FAR + (1.0 - self.BLUR_FAR) * sharp
        r = min(self.R_STEPS, key=lambda s: abs(s - r))
        if r >= 0.999:
            self._draw_shapes(screen, ax, ay, zoom, 1.0, u)
            return
        buf = self._buffer(r)
        buf.fill(self.sky)
        self._draw_shapes(buf, ax, ay, zoom, r, u)
        screen.blit(pygame.transform.smoothscale(buf, (self.width, self.height)), (0, 0))

    # ------------------------------------------------------------ collision data
    def summit_geometry(self, camera_x, camera_y, feet):
        """Return (world left, world right, top height, cabin world rect, anchored)."""
        ax, ay, zoom, f = self._transform(camera_x, camera_y, feet)
        half = self.plateau_half * zoom
        cx_world = ax + camera_x
        top_h = self.ground - (ay + camera_y)
        hx, hy, hw, hh = self.house_img
        hx_world = ax + (hx - self.cx) * zoom + camera_x
        hy_screen = ay + (hy - self.peak_y) * zoom
        hy_world = self.ground - (hy_screen + camera_y)
        rect = pygame.Rect(int(hx_world), int(self.ground - hy_world),
                           int(hw * zoom), int(hh * zoom))
        return (cx_world - half, cx_world + half, top_h, rect, f >= 0.92)
