#!/usr/bin/python


class Command:

    STANDBY = 0         # Command states
    EDITING = 1
    DONE = 2

    def __init__(self):
        self.state = self.STANDBY

    def start(self):
        return

    def process_move(self, x, y):
        # print('command.process_move')
        return

    def process_click(self, event, x, y, image_panel):
        """ Process a valid click on the image.
        :returns is_done True = command has been executed successfully.
        """
        return False

    def plot(self, axes):
        return