import pyglet

from pglib.geometry.point import Point2d
from pglib.draw.pyglet.drawables import Grid
from pglib.draw.pyglet import utils


class AppBase(pyglet.window.Window):

    def __init__(self, root_node, grid_spacing, *args, **kwargs):
        super(AppBase, self).__init__(*args, **kwargs)

        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(
            pyglet.gl.GL_SRC_ALPHA,
            pyglet.gl.GL_ONE_MINUS_SRC_ALPHA
        )

        self.root_node = root_node
        self.grid_spacing = grid_spacing
        self.grid = Grid(
            self.grid_spacing,
            Point2d(0, 0),
            Point2d(self.width, self.height),
            colour=None,
            line_colour=(0.25, 0.25, 0.25, 1)
        )

    def refresh(self):
        self.root_node.evaluate()
        self.drawables = utils.get_drawables(
            self.root_node,
            self.grid_spacing
        )

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.F5:
            self.refresh()

    def on_draw(self):
        self.clear()
        self.grid.draw()
        for drawable in self.drawables:
            drawable.draw()

    def run(self):
        self.refresh()
        pyglet.app.run()