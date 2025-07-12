import RPi.GPIO as GPIO
class lock:
    def __init__(self, pin,door):
        self.pin = pin
        self.door = door
        
    def registerEventListener():
        