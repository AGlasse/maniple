#!/usr/bin/python
from source.command.command import Command


class CropCommand(Command):

    def __init__(self):
        Command.__init__(self)
        return

    def start(self, x, y):
        self.box = [x, y, x, y]  # Initialise crop box
        self.state = self.EDITING
        return

    def plot(self, ax):
        b = self.box
        xb = [b[0], b[2], b[2], b[0], b[0]]
        yb = [b[1], b[1], b[3], b[3], b[1]]
        ax.plot(xb, yb, color='green')
#        print("Crop button is plotting x={:5.1f}-{:<5.1f} y={:5.1f}-{:<5.1f}".format(b[0], b[2], b[1], b[3]))
        return

    def mouse_motion(self, x, y):
        if self.state is self.EDITING:      # Refresh box end coordinates
            self.box[2:] = [x, y]
        return

    def mouse_button_pressed(self, event, x, y, image_panel):
        state = self.state
        is_done = False
        if state is self.EDITING:
            image_panel.croptobox(self.box)
            state = self.STANDBY
            is_done = True
        else:
            print('cropCommand - no valid state')
        self.state = state
        return is_done

    def mouse_button_released(self, event):
        print("Crop button released")
        return
