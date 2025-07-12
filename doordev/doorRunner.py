from flask import Flask, render_template, request, jsonify
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
    19: {'name': 'GPIO 19', 'state': GPIO.LOW, 'led': 20, 'override': False},
    13: {'name': 'GPIO 13', 'state': GPIO.LOW, 'led': 26, 'override': False}
}

buttons = {
    16: {'name': 'button1'},
    12: {'name': 'button2'}
}

for pin in doors:
    print("setting door" + str(pin))
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    ledPin = doors[pin]['led']
    GPIO.setup(ledPin, GPIO.OUT)
    GPIO.output(ledPin, GPIO.LOW)


def getDoorState(pin):
    """Return the current state of the door relay pin."""
    print("getting door state" + str(pin))
    state = GPIO.input(pin)
    return state


@app.route('/state')
def state():
    """Return the current state of all doors as JSON."""
    print("getting state")
    return jsonify(doors)


@app.route('/override/<door>')
def override(door):
    """Toggle override for a specific door by index."""
    try:
        keys = list(doors)
        door_idx = int(door)
        if door_idx < 0 or door_idx >= len(keys):
            return jsonify({'error': 'Invalid door index'}), 400
        doorPin = keys[door_idx]
        doors[doorPin]['override'] = not doors[doorPin]['override']
        print(
            f"Overriding door {doorPin}, new override state: {doors[doorPin]['override']}")
        return jsonify(doors[doorPin])
    except (ValueError, IndexError):
        return jsonify({'error': 'Invalid door index'}), 400


@app.route('/lock')
def lock():
    """Lock all doors that are not overridden."""
    print("locking")
    global locked
    locked = True
    for pin in doors:
        if not doors[pin]['override']:
            GPIO.output(pin, GPIO.HIGH)
            doors[pin]['state'] = getDoorState(pin)
            ledPin = doors[pin]['led']
            GPIO.output(ledPin, GPIO.HIGH)
    return "locked"


@app.route('/unlock')
def unlock():
    """Unlock all doors that are not overridden."""
    print("unlocking")
    global locked
    locked = False
    for pin in doors:
        if not doors[pin]['override']:
            GPIO.output(pin, GPIO.LOW)
            doors[pin]['state'] = getDoorState(pin)
            ledPin = doors[pin]['led']
            GPIO.output(ledPin, GPIO.LOW)
    return "unlocked"


def button_callback(pin):
    """Handle button press events to toggle lock state."""
    print("Button was pushed!" + str(pin))
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
    GPIO.add_event_detect(
        pin, GPIO.RISING, callback=button_callback, bouncetime=80)

if __name__ == '__main__':
    # Debug/Development
    # app.run(debug=True, host="0.0.0.0", port="5000")
    # Production
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()


def exit_handler():
    """Clean up GPIO settings on exit."""
    GPIO.cleanup()


atexit.register(exit_handler)
