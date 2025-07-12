import RPi.GPIO as GPIO
import lock
class Door:
    def __init__(self, pin, state):
        self.pin = pin
        self.state=state
        