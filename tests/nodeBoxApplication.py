from functools import partial

import nodebox.graphics as nbg
import nodebox.graphics.context as nbc


def grid( width, height, spacing, stroke ):
    for x in range( 0, width, spacing ):
        nbg.line( x, 0, x, height, stroke=stroke )
    for y in range( 0, height, spacing ):
        nbg.line( 0, y, width, y, stroke=stroke )


class NodeBoxApplication( object ):

    def __init__( self, width=500, height=500, gridSpacing=10 ):
        self.width = width
        self.height = height
        self.gridSpacing = gridSpacing

        self.canvas = nbc.Canvas( self.width, self.height )
        self.drawFns = self.getDrawFunctions()

        self.mode = 0

        def draw( canvas ):
            canvas.clear()
            nbg.rect( 0, 0, canvas.width, canvas.height )
            grid( width, height, self.gridSpacing, (0.25, 0.25, 0.25, 1) )
            if canvas.keys and len( canvas.keys ) == 1:
                key = canvas.keys[0]
                if key == 'f5' or key.isdigit():
                    if key.isdigit():
                        self.mode = key
                    self.drawFns = self.getDrawFunctions()
            for drawFn in self.drawFns:
                drawFn()

        self.canvas.run( draw )

    def getDrawFunctions( self ):
        return []

    def regionToRect( self, region, **kwargs ):
        x = region.x1 * self.gridSpacing
        y = region.y1 * self.gridSpacing
        w = region.width * self.gridSpacing
        h = region.height * self.gridSpacing
        return partial( nbg.rect, *[x, y, w, h], **kwargs )


if __name__ == '__main__':

    GRID_SPACING = 10
    SCREEN_WIDTH = 500
    SCREEN_HEIGHT = 400

    NodeBoxApplication( SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SPACING )