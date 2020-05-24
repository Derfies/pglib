import math
import copy

import pandac.PandaModules as pm
from direct.showbase.ShowBase import ShowBase
from direct.directtools.DirectGrid import DirectGrid

import p3d
from p3d import geometry
from pglib.test import Volume, Columns, Box, DivideX, DivideY, DivideZ# as BoxGen


GRID_SIZE = 50


class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        self.set_up_grid()
        self.set_up_lights()
        self.set_up_helpers()

        v = Volume(10, 20, 30)
        v.matrix.rotate(25, (-1, -1, -1))
        v.matrix.translate_x(15)
        v.matrix.translate_y(0)
        v.matrix.translate_z(0)
        v.matrix.scale_x(1.5)
        self.create_box(v)

        #return

        #print v
        b = Box(v)
        for s in b.select('sides'):
            d = DivideZ(3, s)
            for c in d.select('all'):
                self.create_box(c)

        # for s in b.select('top'):
        #     d = DivideY(3, s)
        #     for c in d.select('all'):
        #         self.create_box(c)




    def create_box(self, v):
        x, y, z = v.dimensions
        b = geometry.Box(x, y, z,
            origin=-pm.Point3(v.x / 2.0, v.y / 2.0, v.z / 2.0)
        )
        box = pm.NodePath(b)
        box.setRenderModeWireframe()
        box.setTwoSided(True)
        box.reparentTo(self.render)

        m = pm.LMatrix4f(*v.matrix.array.flatten())
        m.transposeInPlace()
        box.setMat(m)

        s = loader.loadModel('smiley')
        s.reparentTo(self.render)

        fix_model_scale = pm.LMatrix4f().scaleMat(0.5)
        fix_model_pos = pm.LMatrix4f().translateMat(1, 1, 1)
        dimension_scale = pm.LMatrix4f().scaleMat(pm.LVecBase3f(v.x, v.y, v.z))
        m = fix_model_pos * dimension_scale * fix_model_scale * m
        s.setMat(m)

    def set_up_lights(self):
        dlight = pm.DirectionalLight('dlight1')
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(35, -75, 0)
        self.render.setLight(dlnp)

        dlight = pm.DirectionalLight('dlight1')
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(35, -105, 0)
        self.render.setLight(dlnp)

    def set_up_grid(self):
        """Create the grid and set up its appearance."""
        self.grid = DirectGrid(
            gridSize=GRID_SIZE,
            gridSpacing=1.0,
            planeColor=(0.5, 0.5, 0.5, 0.0),
            parent=self.render
        )
        self.grid.snapMarker.hide()
        self.grid.centerLines.setColor((0, 0, 0, 0))
        self.grid.centerLines.setThickness(2)
        self.grid.majorLines.setColor((0.25, 0.25, 0.25, 0))
        self.grid.majorLines.setThickness(1)
        self.grid.minorLines.setColor((0.5, 0.5, 0.5, 0))
        self.grid.updateGrid()

    def set_up_helpers(self):
        # Axes.
        box = pm.NodePath(p3d.geometry.Box())
        box.setColor(1, 0, 0, 1)
        box.setPos(GRID_SIZE + 2, 0, 0)
        #box.setScale(0.5)
        box.reparentTo(self.render)

        box = pm.NodePath(p3d.geometry.Box())
        box.setColor(0, 1, 0, 1)
        box.setPos(0, GRID_SIZE + 2, 0)
        #box.setScale(0.5)
        box.reparentTo(self.render)

        box = pm.NodePath(p3d.geometry.Box())
        box.setColor(0, 0, 1, 1)
        box.setPos(0, 0, GRID_SIZE + 2)
        #box.setScale(0.5)
        box.reparentTo(self.render)


app = MyApp()
app.run()