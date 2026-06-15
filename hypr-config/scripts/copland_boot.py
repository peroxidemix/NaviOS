
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gtk, Gdk, GLib, GtkLayerShell
import cairo
import math
import random

DURATION = 8.0
FPS = 30

NAVY     = (0.015, 0.02, 0.07)
CYAN     = (0.42, 0.85, 0.90)
CYAN_DIM = (0.18, 0.40, 0.50)
PINK     = (0.85, 0.45, 0.65)
WHITE    = (0.85, 0.90, 0.95)

LOG_FRAGMENTS = [
    "INIT::wired_link",
    "node_sync ... ok",
    "layer 07",
    "protocol/7",
    "auth: ----",
    "0x7F3A",
    "scanning...",
    "buffer ok",
    "sync 99.2%",
    "link established",
    ">> connect",
    "tachibana//lab",
    "process: lain",
    "memory ok",
    "render: ok",
]


class Particle:
    def __init__(self, w, h):
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        self.speed = random.uniform(8, 30)
        self.size = random.uniform(0.5, 2.0)
        self.bright = random.uniform(0.2, 0.8)

    def update(self, dt, w, h):
        self.y -= self.speed * dt
        if self.y < 0:
            self.y = h
            self.x = random.uniform(0, w)


class Splash(Gtk.Window):
    def __init__(self):
        super().__init__()
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.EXCLUSIVE)
        for edge in (GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.BOTTOM,
                     GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT):
            GtkLayerShell.set_anchor(self, edge, True)

        self.set_app_paintable(True)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)

        self.connect("draw", self.on_draw)
        self.connect("key-press-event", self.on_key)
        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)

        self.start_time = GLib.get_monotonic_time() / 1_000_000.0
        self.last_time = self.start_time
        self.particles = None  # init on first draw once we know size

        self.fragments = []  # list of (text, x, y, spawn_time, lifetime)
        self.last_frag_spawn = 0.0

        self.glitch_until = 0.0
        self.next_glitch = random.uniform(1.0, 2.0)

        GLib.timeout_add(int(1000 / FPS), self.on_tick)
        self.show_all()

    def on_key(self, widget, event):
        Gtk.main_quit()
        return True

    def on_tick(self):
        elapsed = GLib.get_monotonic_time() / 1_000_000.0 - self.start_time
        if elapsed >= DURATION:
            Gtk.main_quit()
            return False
        self.queue_draw()
        return True

    def on_draw(self, widget, ctx):
        alloc = self.get_allocation()
        w, h = alloc.width, alloc.height
        cx, cy = w / 2, h * 0.40

        now = GLib.get_monotonic_time() / 1_000_000.0
        elapsed = now - self.start_time
        dt = now - self.last_time
        self.last_time = now
        t = elapsed

        if self.particles is None:
            self.particles = [Particle(w, h) for _ in range(80)]

        alpha = 1.0
        if t < 0.6:
            alpha = t / 0.6
        elif t > DURATION - 1.2:
            alpha = max(0.0, (DURATION - t) / 1.2)

        ctx.set_source_rgba(*NAVY, alpha)
        ctx.paint()

        horizon = h * 0.62
        ctx.set_source_rgba(*CYAN_DIM, 0.35 * alpha)
        ctx.set_line_width(1)
        n_lines = 14
        for i in range(-n_lines, n_lines + 1):
            x_far = cx + i * (w * 0.02)
            x_near = cx + i * (w * 0.12)
            ctx.move_to(x_far, horizon)
            ctx.line_to(x_near, h)
            ctx.stroke()
        scroll = (t * 0.15) % 1.0
        for j in range(8):
            frac = (j + scroll) / 8.0
            y = horizon + (h - horizon) * (frac ** 2)
            ctx.set_source_rgba(*CYAN_DIM, (0.4 * (1 - frac)) * alpha)
            ctx.move_to(0, y)
            ctx.line_to(w, y)
            ctx.stroke()

        for p in self.particles:
            p.update(dt, w, h)
            ctx.set_source_rgba(*CYAN, p.bright * alpha)
            ctx.rectangle(p.x, p.y, p.size, p.size)
            ctx.fill()

        radius = min(w, h) * 0.16
        rot = t * 0.6

        for i, squash in enumerate([1.0, 0.45, 0.45, 0.7]):
            ctx.save()
            ctx.translate(cx, cy)
            ctx.rotate(rot + i * (math.pi / 3))
            ctx.scale(1.0, squash)
            ctx.set_source_rgba(*CYAN, 0.5 * alpha)
            ctx.set_line_width(1.4)
            ctx.arc(0, 0, radius, 0, 2 * math.pi)
            ctx.stroke()
            ctx.restore()

        for i in range(60):
            a = rot * 1.5 + i * (2 * math.pi / 60)
            r = radius * 1.6
            x = cx + r * math.cos(a)
            y = cy + r * math.sin(a) * 0.4
            ctx.set_source_rgba(*CYAN, 0.4 * alpha)
            ctx.rectangle(x, y, 1.5, 1.5)
            ctx.fill()

        ctx.set_source_rgba(*CYAN, 0.85 * alpha)
        ctx.set_line_width(1.6)
        ctx.arc(cx, cy, radius * 0.55, 0, 2 * math.pi)
        ctx.stroke()

        for frac in (0.33, 0.66):
            ctx.save()
            ctx.translate(cx, cy)
            ctx.scale(1.0, frac)
            ctx.set_source_rgba(*CYAN_DIM, 0.6 * alpha)
            ctx.set_line_width(1)
            ctx.arc(0, 0, radius * 0.55, 0, 2 * math.pi)
            ctx.stroke()
            ctx.restore()

        for k in range(3):
            ctx.save()
            ctx.translate(cx, cy)
            ctx.rotate(rot * 0.5 + k * (math.pi / 3))
            ctx.scale(0.4, 1.0)
            ctx.set_source_rgba(*CYAN_DIM, 0.5 * alpha)
            ctx.set_line_width(1)
            ctx.arc(0, 0, radius * 0.55, 0, 2 * math.pi)
            ctx.stroke()
            ctx.restore()

        cross_r = radius * 0.12
        ctx.set_source_rgba(*CYAN, 0.9 * alpha)
        ctx.set_line_width(1.2)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ctx.move_to(cx + dx * cross_r, cy + dy * cross_r)
            ctx.line_to(cx + dx * cross_r * 1.8, cy + dy * cross_r * 1.8)
            ctx.stroke()

        bracket = 28
        margin = 24
        ctx.set_source_rgba(*CYAN, 0.6 * alpha)
        ctx.set_line_width(1.5)
        for (bx, by, dx, dy) in [
            (margin, margin, 1, 1),
            (w - margin, margin, -1, 1),
            (margin, h - margin, 1, -1),
            (w - margin, h - margin, -1, -1),
        ]:
            ctx.move_to(bx, by + dy * bracket)
            ctx.line_to(bx, by)
            ctx.line_to(bx + dx * bracket, by)
            ctx.stroke()

        ctx.save()
        ctx.translate(w * 0.16, h * 0.20)
        ctx.rotate(-0.32)
        ctx.set_source_rgba(*CYAN, 0.9 * alpha)
        ctx.select_font_face("monospace", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(30)
        ctx.show_text("Copland OS Enterprise")
        ctx.set_font_size(15)
        ctx.move_to(0, 28)
        ctx.set_source_rgba(*CYAN_DIM, 0.9 * alpha)
        ctx.show_text("Product by Tachibana Lab.")
        ctx.restore()

        ctx.set_source_rgba(*CYAN, 0.85 * alpha)
        ctx.select_font_face("monospace", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(26)
        ctx.move_to(w * 0.05, h * 0.80)
        ctx.show_text("...Enterprise Os....")

        ctx.set_source_rgba(*CYAN_DIM, 0.8 * alpha)
        ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(12)
        ctx.move_to(margin + 6, h - margin - 8)
        ctx.show_text(f"BOOT SEQUENCE :: t+{t:5.2f}s")

        if t - self.last_frag_spawn > 0.35 and len(self.fragments) < 6:
            self.last_frag_spawn = t
            text = random.choice(LOG_FRAGMENTS)
            fx = random.uniform(w * 0.05, w * 0.85)
            fy = random.uniform(h * 0.08, h * 0.55)
            self.fragments.append([text, fx, fy, t, random.uniform(0.4, 0.9)])

        ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(13)
        new_fragments = []
        for frag in self.fragments:
            text, fx, fy, spawn, life = frag
            age = t - spawn
            if age < life:
                fa = (1 - age / life) * alpha
                ctx.set_source_rgba(*CYAN, 0.7 * fa)
                ctx.move_to(fx, fy)
                ctx.show_text(text)
                new_fragments.append(frag)
        self.fragments = new_fragments

        if t > self.glitch_until:
            if random.random() < 0.02:
                self.glitch_until = t + random.uniform(0.04, 0.12)
        if t < self.glitch_until:
            for _ in range(random.randint(2, 5)):
                gy = random.uniform(0, h)
                gh = random.uniform(2, 14)
                gx_off = random.uniform(-30, 30)
                ctx.save()
                ctx.rectangle(0, gy, w, gh)
                ctx.clip()
                ctx.translate(gx_off, 0)
                ctx.set_source_rgba(*CYAN, 0.15 * alpha)
                ctx.paint()
                ctx.restore()

        if t > 2.0:
            lain_alpha = min(1.0, (t - 2.0) / 1.0) * alpha
            ctx.set_source_rgba(*PINK, lain_alpha)
            ctx.select_font_face("sans-serif", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(36)
            ctx.move_to(w * 0.55, h * 0.80)
            ctx.show_text("lain")

        ctx.set_source_rgba(0, 0, 0, 0.18 * alpha)
        y = 0
        while y < h:
            ctx.rectangle(0, y, w, 1)
            ctx.fill()
            y += 3

        grad = cairo.RadialGradient(cx, h * 0.5, h * 0.2, cx, h * 0.5, h * 0.9)
        grad.add_color_stop_rgba(0, 0, 0, 0, 0)
        grad.add_color_stop_rgba(1, 0, 0, 0, 0.55 * alpha)
        ctx.set_source(grad)
        ctx.paint()

        return False


if __name__ == "__main__":
    win = Splash()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()
