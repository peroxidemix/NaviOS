
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gtk, Gdk, GLib, GtkLayerShell
import cairo
import math
import subprocess


NODES = [
    {"label": "firefox",  "cmd": "firefox"},
    {"label": "spotify",  "cmd": "spotify"},
    {"label": "ryujinx",  "cmd": "flatpak run io.github.ryubing.Ryujinx"},
]

AMBER       = (0.91, 0.66, 0.40)   # #e8a866
AMBER_DIM   = (0.42, 0.27, 0.10)
CYAN        = (0.36, 0.88, 0.90)   # #5ce1e6
RING_RADIUS_FRAC = 0.22            # fraction of min(width,height)
NODE_RADIUS = 46
LINE_WIDTH  = 1.4


class Navi(Gtk.Window):
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
        self.connect("button-press-event", self.on_click)
        self.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
        )
        self.connect("motion-notify-event", self.on_motion)

        self.tick = 0
        self.hover = -1
        self.node_positions = []  # filled in on_draw

        GLib.timeout_add(33, self.on_tick)  # ~30fps

        self.show_all()

    def on_tick(self):
        self.tick += 1
        self.queue_draw()
        return True

    def on_key(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()
        return True

    def on_motion(self, widget, event):
        mx, my = event.x, event.y
        self.hover = -1
        for i, (cx, cy) in enumerate(self.node_positions):
            if (mx - cx) ** 2 + (my - cy) ** 2 <= NODE_RADIUS ** 2:
                self.hover = i
                break
        return True

    def on_click(self, widget, event):
        mx, my = event.x, event.y
        for i, (cx, cy) in enumerate(self.node_positions):
            if (mx - cx) ** 2 + (my - cy) ** 2 <= NODE_RADIUS ** 2:
                cmd = NODES[i]["cmd"]
                subprocess.Popen(["sh", "-c", cmd])
                Gtk.main_quit()
                return True
        Gtk.main_quit()
        return True

    def on_draw(self, widget, ctx):
        alloc = self.get_allocation()
        w, h = alloc.width, alloc.height
        cx0, cy0 = w / 2, h / 2

        ctx.set_source_rgba(0.02, 0.01, 0.0, 0.35)
        ctx.paint()

        radius = min(w, h) * RING_RADIUS_FRAC
        n = len(NODES)

        ctx.set_source_rgba(*AMBER_DIM, 0.5)
        ctx.set_line_width(1)
        ctx.arc(cx0, cy0, radius, 0, 2 * math.pi)
        ctx.stroke()

        rot = self.tick * 0.004
        for i in range(36):
            a = rot + i * (2 * math.pi / 36)
            r1 = radius - 4
            r2 = radius + (8 if i % 3 == 0 else 4)
            x1, y1 = cx0 + r1 * math.cos(a), cy0 + r1 * math.sin(a)
            x2, y2 = cx0 + r2 * math.cos(a), cy0 + r2 * math.sin(a)
            ctx.set_source_rgba(*AMBER_DIM, 0.6)
            ctx.set_line_width(1)
            ctx.move_to(x1, y1)
            ctx.line_to(x2, y2)
            ctx.stroke()

        pulse = 0.5 + 0.5 * math.sin(self.tick * 0.05)
        ctx.set_source_rgba(*CYAN, 0.15 + 0.15 * pulse)
        ctx.arc(cx0, cy0, 18 + 4 * pulse, 0, 2 * math.pi)
        ctx.fill()
        ctx.set_source_rgba(*CYAN, 0.9)
        ctx.set_line_width(1.5)
        ctx.arc(cx0, cy0, 10, 0, 2 * math.pi)
        ctx.stroke()

        self.node_positions = []
        for i, node in enumerate(NODES):
            angle = -math.pi / 2 + i * (2 * math.pi / n)
            nx = cx0 + radius * math.cos(angle)
            ny = cy0 + radius * math.sin(angle)
            self.node_positions.append((nx, ny))

            is_hover = (i == self.hover)
            col = CYAN if is_hover else AMBER

            ctx.set_source_rgba(*AMBER_DIM, 0.7)
            ctx.set_line_width(LINE_WIDTH)
            ctx.move_to(cx0, cy0)
            ctx.line_to(nx, ny)
            ctx.stroke()

            self.draw_hex(ctx, nx, ny, NODE_RADIUS, col, is_hover)

            ctx.set_source_rgba(*col, 1.0)
            ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(15)
            text = node["label"]
            extents = ctx.text_extents(text)
            ctx.move_to(nx - extents.width / 2, ny + NODE_RADIUS + 22)
            ctx.show_text(text)

        return False

    def draw_hex(self, ctx, cx, cy, r, color, hover):
        ctx.new_path()
        for i in range(6):
            a = math.pi / 6 + i * (math.pi / 3)
            x, y = cx + r * math.cos(a), cy + r * math.sin(a)
            if i == 0:
                ctx.move_to(x, y)
            else:
                ctx.line_to(x, y)
        ctx.close_path()

        if hover:
            ctx.set_source_rgba(*color, 0.18)
            ctx.fill_preserve()

        ctx.set_source_rgba(*color, 0.9 if hover else 0.7)
        ctx.set_line_width(2 if hover else 1.5)
        ctx.stroke()

        ctx.new_path()
        ir = r * 0.6
        for i in range(6):
            a = math.pi / 6 + i * (math.pi / 3)
            x, y = cx + ir * math.cos(a), cy + ir * math.sin(a)
            if i == 0:
                ctx.move_to(x, y)
            else:
                ctx.line_to(x, y)
        ctx.close_path()
        ctx.set_source_rgba(*color, 0.4)
        ctx.set_line_width(1)
        ctx.stroke()


if __name__ == "__main__":
    win = Navi()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()
