#!/usr/bin/python


class Command:

    STANDBY = 0         # Command states
    EDITING = 1
    DONE = 2

    def __init__(self):
        self.state = self.STANDBY

    def start(self, x, y):
        print("Command.start not defined")
        return

    def plot(self, ax):
        print("Command.plot not defined")
        return

    def mouse_motion(self, x, y):
        print("Command.mouse_motion not defined")
        return

    def mouse_button_pressed(self, event, x, y, image_panel):
        print("Command.mouse_button_process not defined")
        is_done = False
        return is_done

    def mouse_button_released(self, event):
        print("Command.mouse_button_released not defined")
        return
