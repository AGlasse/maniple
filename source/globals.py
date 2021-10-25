#!/usr/bin/python
import os
from buffer import Buffer

class Globals:

    execution_directory = None
    buffers = {'A': Buffer(), 'B': Buffer()}
    display_buffer_name = 'A'


    def __init__(self):
        Globals.execution_directory = os.getcwd()

    @staticmethod
    def load_buffer(buffer_name, block):
        Globals.buffers[buffer_name].set(block)
        return

    @staticmethod
    def set_display_buffer(buffer_name):
#        print('Setting display to buffer ' + Globals.display_buffer_name)
        Globals.display_buffer_name = buffer_name
        return

    @staticmethod
    def get_display_buffer():
#        print('Displaying buffer ' + Globals.display_buffer_name)
        buffer = Globals.buffers[Globals.display_buffer_name]
        return buffer
