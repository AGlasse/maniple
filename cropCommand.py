#!/usr/bin/python
from command import Command


class CropCommand(Command):

    def __init__(self):
        Command.__init__(self)
        self.start()

    def start(self):
        self.box = []
        self.state = self.STANDBY

    def plot(self, axes):
        if self.state is self.EDITING:
            b = self.box
            xb = [b[0], b[2], b[2], b[0], b[0]]
            yb = [b[1], b[1], b[3], b[3], b[1]]
            axes.plot(xb, yb, color='green')

    def process_move(self, x, y):
        if self.state is self.EDITING:      # Refresh box end coordinates
            self.box[2:] = [x, y]

    def process_click(self, event, x, y, image_panel):
        state = self.state
        is_done = False
        if state is self.STANDBY:           # Start editing geometry
            self.box = [x, y, x, y]         # Initialise crop box
            state = self.EDITING
        else:
            if state is self.EDITING:
                image_panel.croptobox(self.box)
                state = self.STANDBY
                is_done = True
            else:
                print('- no valid state')
        self.state = state
        return is_done
