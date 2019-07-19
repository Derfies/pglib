import math


class SineWeight(object):

    def __init__(self, amplitude, invert=False):
        self.amplitude = amplitude
        self.invert = invert
    
    def __call__(self, x):
        value = math.sin(math.radians(x))
        if self.invert:
            value = 1 - value
        return pow(value, self.amplitude)