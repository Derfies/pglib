from pglib import utils, Region, randomRegions
from nodeBoxApplication import NodeBoxApplication


class App( NodeBoxApplication ):
    
    def getDrawFunctions( self ):
        pRegion = Region( 0, 0, self.width / self.gridSpacing, self.height / self.gridSpacing )
        return [
            self.regionToRect( region, fill=utils.getRandomColour( a=1 ) )
            for region in randomRegions( pRegion, 5, 10, 300, False )
        ]


if __name__ == '__main__':

    GRID_SPACING = 10
    SCREEN_WIDTH = 64 * GRID_SPACING
    SCREEN_HEIGHT = 48 * GRID_SPACING

    App( SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SPACING )