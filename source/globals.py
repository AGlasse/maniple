#!/usr/bin/python
import os
import copy
import numpy as np


class Globals:

    execution_directory = None

    def __init__(self):
        Globals.execution_directory = os.getcwd()
        Globals.buffers = {'A': Buffer(), 'B': Buffer()}
        return

    @staticmethod
    def load_buffer(buffer_name, block):
        Globals.buffers[buffer_name].set(block)
        return

    @staticmethod
    def get_buffer(buffer_name):
        #        print('Displaying buffer ' + Globals.display_buffer_name)
        buffer = Globals.buffers[buffer_name]
        return buffer


class Buffer:
    """ Data cube and associated parameters.  The default object holds a test
    pattern.
    """

    def __init__(self):
        """ Initialise data buffer with a block containing two data cubes,
        each comprising three 40 x 40 images. For MIRI LV2 data, these
        correspond to ints x frames x rows x columns.
        """
        self.block = np.random.rand(2, 3, 40, 50)  # 2 x 3 x 40 x 50 images
        return

    def get(self):
        return self.block

    def set(self, block):
        self.block = copy.deepcopy(block)
        return

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
