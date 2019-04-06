from pglib import utils, Region, bspRegions
from nodeBoxApplication import NodeBoxApplication


MIN_LEAF_SIZE = 6
MAX_LEAF_SIZE = 20


class App( NodeBoxApplication ):
    
    def getDrawFunctions( self ):
        pRegion = Region( 0, 0, self.width / self.gridSpacing, self.height / self.gridSpacing )
        return [
            self.regionToRect( region, fill=utils.getRandomColour( a=1 ) )
            for region in bspRegions( pRegion, MIN_LEAF_SIZE, MAX_LEAF_SIZE )
        ]


if __name__ == '__main__':

    GRID_SPACING = 10
    SCREEN_WIDTH = 64 * GRID_SPACING
    SCREEN_HEIGHT = 48 * GRID_SPACING

    App( SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SPACING )