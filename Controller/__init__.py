import pygame as py


class Controller:
    def __init__(self):
        py.joystick.init()
        self.joystick_count = py.joystick.get_count()
        self.joysticks = []
        for i in range(self.joystick_count):
            joystick = py.joystick.Joystick(i)
            joystick.init()
            self.joysticks.append(joystick)

    def get_joystick_count(self):
        return self.joystick_count

    def get_joystick(self, index):
        if 0 <= index < self.joystick_count:
            return self.joysticks[index]
        else:
            raise IndexError("Joystick index out of range")

    def get_button_state(self, joystick_index, button_index):
        joystick = self.get_joystick(joystick_index)
        if 0 <= button_index < joystick.get_numbuttons():
            return joystick.get_button(button_index)
        else:
            raise IndexError("Button index out of range")

    def get_axis_state(self, joystick_index, axis_index):
        joystick = self.get_joystick(joystick_index)
        if 0 <= axis_index < joystick.get_numaxes():
            return joystick.get_axis(axis_index)
        else:
            raise IndexError("Axis index out of range")