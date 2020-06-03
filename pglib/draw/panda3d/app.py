import pandac.PandaModules as pm
from direct.showbase.ShowBase import ShowBase
from direct.directtools.DirectGrid import DirectGrid

from pglib.shape import Scope
from pglib.draw.appbase import AppBase
from pglib.geometry.vector import Vector3
import p3d
from p3d import geometry


GRID_SIZE = 50


class App(ShowBase, AppBase):

    def __init__(self, shape, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)



        self.set_up_grid()
        self.set_up_lights()
        self.set_up_helpers()

        #s = Scope(0.1, 0.1, 1)
        #s.translation = Vector3(-0.05, -0.05, 0.0)
        #self.create_scope_box(s)


        def do_shape(shape):


            # for i, scope in enumerate(shape.stack):
            #     print 'stack:', i, scope.translation, scope.size
            #     self.create_scope_box(scope)

            for i, scope in enumerate(shape.keep):
                print 'keep:', i, scope.translation, scope.size
                self.create_scope_box(scope)

            for sub_shape in shape.sub_shapes:
                do_shape(sub_shape)

        do_shape(shape)

    def create_scope_box(self, t):
        x, y, z = t.size
        b = geometry.Box(x, y, z, origin=-pm.Point3(*t.size / 2))
        box = pm.NodePath(b)
        box.setRenderModeWireframe()
        box.setTwoSided(True)
        box.reparentTo(self.render)

        #print t.world_matrix.array

        m = pm.LMatrix4f(*t.world_matrix.array.flatten())
        m.transposeInPlace()
        box.setMat(m)

    def create_box(self, v):
        x, y, z, _ = v.dimensions
        b = geometry.Box(x, y, z)#, origin=-pm.Point3(*(v.dimensions / 2.0)[:3]))
        box = pm.NodePath(b)
        box.setRenderModeWireframe()
        box.setTwoSided(True)
        box.reparentTo(self.render)

        m = pm.LMatrix4f(*v.matrix.array.flatten())
        m.transposeInPlace()
        box.setMat(m)

        return

        s = loader.loadModel('smiley')
        s.reparentTo(self.render)

        fix_model_scale = pm.LMatrix4f().scaleMat(0.5)
        #fix_model_pos = pm.LMatrix4f().translateMat(1, 1, 1)
        dimension_scale = pm.LMatrix4f().scaleMat(pm.LVecBase3f(x, y, z))
        #m = fix_model_pos * dimension_scale * fix_model_scale * m
        m = dimension_scale * fix_model_scale * m
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

    #def run(self):
    #    self.run()