import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, GtkLayerShell

def make_bar(edge):
    win = Gtk.Window()
    GtkLayerShell.init_for_window(win)
    GtkLayerShell.set_layer(win, GtkLayerShell.Layer.OVERLAY)
    GtkLayerShell.set_anchor(win, GtkLayerShell.Edge.LEFT, True)
    GtkLayerShell.set_anchor(win, GtkLayerShell.Edge.RIGHT, True)
    GtkLayerShell.set_anchor(win, edge, True)
    GtkLayerShell.set_exclusive_zone(win, 0)

    screen = win.get_screen()
    visual = screen.get_rgba_visual()
    if visual and screen.is_composited():
        win.set_visual(visual)
    win.set_app_paintable(True)

    win.set_default_size(-1, 4)
    box = Gtk.Box()
    box.get_style_context().add_class("navibar")
    win.add(box)

    css = Gtk.CssProvider()
    css.load_from_data(b"""
        .navibar {
            background-color: rgba(126, 200, 212, 0.5);
            min-height: 4px;
        }
    """)
    Gtk.StyleContext.add_provider_for_screen(screen, css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    win.show_all()

make_bar(GtkLayerShell.Edge.TOP)
make_bar(GtkLayerShell.Edge.BOTTOM)
Gtk.main()
