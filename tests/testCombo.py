from functools import partial

import nodebox.graphics as nbg

from pglib import utils, Region, randomRegions, drunkardsWalk
from nodeBoxApplication import NodeBoxApplication


class App( NodeBoxApplication ):
    
    def getDrawFunctions( self ):
        pRegion = Region( 0, 0, self.width / self.gridSpacing, self.height / self.gridSpacing )
        
        drawFns = []
        for region in randomRegions( pRegion, 15, 20, 300, False, value=1 ):
            drunkardsWalk( region )
            colour = utils.getRandomColour( a=1 )
            for x, row in enumerate( region.matrix ):
                for y, cell in enumerate( region.matrix[x] ):
                    if cell:
                        x1 = (region.x1 + x) * self.gridSpacing
                        y1 = (region.y1 + y) * self.gridSpacing
                        size = self.gridSpacing
                        drawFns.append( partial( nbg.rect, *[x1, y1, size, size], fill=colour ) )
        return drawFns


if __name__ == '__main__':

    GRID_SPACING = 10
    SCREEN_WIDTH = 64 * GRID_SPACING
    SCREEN_HEIGHT = 48 * GRID_SPACING

    App( SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SPACING )