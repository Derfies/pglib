import numpy as np
import matplotlib.pyplot as plt


class Perlin(object):

    def run(self, x, y, seed=0):

        # permutation table
        #np.random.seed(seed)
        p = np.arange(256, dtype=int)
        np.random.shuffle(p)
        p = np.stack([p, p]).flatten()

        # coordinates of the top-left
        xi = x.astype(int)
        yi = y.astype(int)

        # internal coordinates
        xf = x - xi
        yf = y - yi

        # fade factors
        u = self.fade(xf)
        v = self.fade(yf)

        # noise components
        n00 = self.gradient(p[p[xi] + yi], xf, yf)
        n01 = self.gradient(p[p[xi] + yi + 1], xf, yf - 1)
        n11 = self.gradient(p[p[xi + 1] + yi + 1], xf - 1, yf - 1)
        n10 = self.gradient(p[p[xi + 1] + yi], xf - 1, yf)

        # combine noises
        x1 = self.lerp(n00, n10, u)
        x2 = self.lerp(n01, n11, u)  # FIX1: I was using n10 instead of n01
        #print int(x1)

        v = self.lerp(x1, x2, v)

        # # Discretise.
        #
        # print v[0]
        # print np.min(v), np.max(v)
        #v = v + 0.5
        #v = np.rint(v)
        #
        # print v[0]
        # print np.min(v), np.max(v)
        return v


        #return lerped  # FIX2: I also had to reverse x1 and x2 here

    def lerp(self, a, b, x):
        "linear interpolation"
        return a + x * (b - a)

    def fade(self, t):
        "6t^5 - 15t^4 + 10t^3"
        return 6 * t ** 5 - 15 * t ** 4 + 10 * t ** 3

    def gradient(self, h, x, y):
        "grad converts h to the right gradient vector and return the dot product with (x,y)"
        vectors = np.array([[0, 1], [0, -1], [1, 0], [-1, 0]])
        g = vectors[h % 4]
        return g[:, :, 0] * x + g[:, :, 1] * y





shape = (100, 100)


octaves = 5
noise = np.zeros(shape)
frequency = 1
amplitude = 1
persistence = 0.5
res = (0.5, 5)
for _ in range(octaves):
    linx = np.linspace(0, frequency * res[0], shape[0], endpoint=False)
    liny = np.linspace(0, frequency * res[1], shape[1], endpoint=False)
    x, y = np.meshgrid(linx, liny)
    noise += amplitude * Perlin().run(x, y)#generate_perlin_noise_2d(shape, (frequency*res[0], frequency*res[1]))
    frequency *= 2
    amplitude *= persistence

# Normalise.
noise = (noise - np.min(noise))/np.ptp(noise)

noise[noise < 0.4] = 0
noise[noise > 0.4] = 1

print np.min(noise)
print np.max(noise)
print noise


plt.imshow(noise, origin='upper')
plt.show()