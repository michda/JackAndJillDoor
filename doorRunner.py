from flask import Flask, render_template, request
from gevent.pywsgi import WSGIServer
import atexit
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

app = Flask(__name__)


# pinmap
# 6 relay 1
# 13 relay 2
# 19 led 1
# 26 led 2
# 20 button 1
# 21 button 2


GPIO.setmode(GPIO.BCM)
locked = False

# the key of doors is the pin attached to the relay
doors = {
    6: {'name': 'GPIO 23', 'state': GPIO.LOW, 'led': 19, 'override': False},
    13: {'name': 'GPIO 24', 'state': GPIO.LOW, 'led': 26, 'override': False}
}

buttons = {
    20: {'name': 'button1'},
    21: {'name': 'button2'}
}

for pin in doors:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
    ledPin = doors[pin]['led']
    GPIO.setup(ledPin, GPIO.OUT)
    GPIO.output(ledPin, GPIO.LOW)


def getDoorState(pin):
    print("getting door state")
    state = GPIO.input(pin)
    return state


@app.route('/state')
def state():
    print("getting state")
    return doors


@app.route('/override/<door>')
def override(door):
    print("overriding door "+str(pin))
    keys = list(doors)
    print(keys)
    doorPin = keys[int(door)]
    doors[doorPin]['override'] = not doors[doorPin]['override']
    return doors[doorPin]


@app.route('/lock')
def lock():
    print("locking")
    global locked
    locked = True
    for pin in doors:
        if not doors[pin]['override']:
            GPIO.output(pin, GPIO.LOW)
            doors[pin]['state'] = getDoorState(pin)
            ledPin = doors[pin]['led']
            GPIO.output(ledPin, GPIO.HIGH)
    return "locked"


@app.route('/unlock')
def unlock():
    print("unlocking")
    global locked
    locked = False
    for pin in doors:
        if not doors[pin]['override']:
            GPIO.output(pin, GPIO.HIGH)
            doors[pin]['state'] = getDoorState(pin)
            ledPin = doors[pin]['led']
            GPIO.output(ledPin, GPIO.LOW)
    return "unlocked"


def button_callback(pin):
    print("Button was pushed!"+str(pin))
    global locked
    if locked:
        locked = False
        unlock()
    else:
        locked = True
        lock()


# Register events
# GPIO.add_event_detect(10,GPIO.RISING,callback=button_callback) # Setup event on pin 10 rising edge
for pin in buttons:
    print("setting buttons")
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # Setup event on pin rising edge
    GPIO.add_event_detect(pin, GPIO.RISING, callback=button_callback)

if __name__ == '__main__':
    # Debug/Development
    # app.run(debug=True, host="0.0.0.0", port="5000")
    # Production
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()


def exit_handler():
    GPIO.cleanup()


atexit.register(exit_handler)
