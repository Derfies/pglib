from functools import partial

import nodebox.graphics as nbg

from pglib import utils, Region, drunkardsWalk
from nodeBoxApplication import NodeBoxApplication


class App( NodeBoxApplication ):
    
    def getDrawFunctions( self ):
        pRegion = Region( 0, 0, self.width / self.gridSpacing, self.height / self.gridSpacing, value=1 )
        drunkardsWalk( pRegion )

        drawFns = []
        for x, row in enumerate( pRegion.matrix ):
            for y, cell in enumerate( pRegion.matrix[x] ):
                if cell:
                    x1 = x * self.gridSpacing
                    y1 = y * self.gridSpacing
                    size = self.gridSpacing
                    drawFns.append( partial( nbg.rect, *[x1, y1, size, size], fill=(1, 0, 0, 1) ) )
        return drawFns


if __name__ == '__main__':

    GRID_SPACING = 10
    SCREEN_WIDTH = 64 * GRID_SPACING
    SCREEN_HEIGHT = 48 * GRID_SPACING

    App( SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SPACING )