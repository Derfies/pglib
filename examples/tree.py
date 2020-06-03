from pglib.draw.panda3d.app import App
from pglib.shape import Shape, AxesSelector, Scope


class Branch(Shape):

    def __init__(self, *args, **kwargs):
        super(Branch, self).__init__(*args, **kwargs)

        if self.scope.size.z < 5:
            return

        self.s(1, 1, 0.9)

        self.push()
        self.ry(25)
        self.rz(25)
        self.i()
        self.tz(self.scope.size.z)
        self.module(Branch)
        self.pop()

        self.push()
        self.ry(-25)
        self.rz(-5)
        self.i()
        self.tz(self.scope.size.z)
        self.module(Branch)
        self.pop()


class Start(Shape):

    def __init__(self, *args, **kwargs):
        super(Start, self).__init__(*args, **kwargs)

        self.s(0.1, 0.1, 1)
        self.center(AxesSelector.XY)
        self.module(Branch)


# Create test app and run.
app = App(Start(Scope(10, 10, 10)))
app.run()