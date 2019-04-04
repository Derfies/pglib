from pglib import utils
from pglib.region import Region
from pglib.randomRegions import RandomRegions
from nodeBoxApplication import NodeBoxApplication


class App( NodeBoxApplication ):
    
    def getDrawFunctions( self ):

        rRegions = RandomRegions()
        rRegions.inputs['region'] = Region( 0, 0, self.width / self.gridSpacing, self.height / self.gridSpacing )
        rRegions.inputs['minSize'] = 5
        rRegions.inputs['maxSize'] = 10
        rRegions.inputs['maxIterations'] = 100
        rRegions.inputs['intersect'] = False

        drawFns = []
        
        for region in rRegions.outputs['regions']:
            drawFns.append( self.regionToRect( region, fill=utils.getRandomColour( a=1) ) )

        return drawFns


if __name__ == '__main__':

    GRID_SPACING = 10
    SCREEN_WIDTH = 64 * GRID_SPACING
    SCREEN_HEIGHT = 48 * GRID_SPACING

    App( SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SPACING )