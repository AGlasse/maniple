#!/usr/bin/python
class Buffer:
    """ Data cube and associated parameters.  The default object holds a test
    pattern.
    """
    def __init__(self):
        """ Initialise data buffer with a block containing two data cubes,
        each comprising three 40 x 40 images. For MIRI LV2 data, these
        correspond to ints x frames x rows x columns.
        """
        import numpy as np

        self.block = np.random.rand(2, 3, 40, 50)   # 2 x 3 x 40 x 50 images
        return

    def get(self):
        return self.block

    def set(self, block):
        self.block = block

    def get_bounds(self):
        """ Return the maximum indices for this buffer.
        """
        czyx = self.block.shape
        xmax = czyx[3]
        ymax = czyx[2]
        zmax = czyx[1]
        cmax = czyx[0]
        return cmax, zmax, ymax, xmax

    def get_frame(self, cube, zslice):
        return self.block[cube, zslice, :, :]
