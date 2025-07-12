from flask import Flask, render_template, request
from gevent.pywsgi import WSGIServer
import atexit

import door
import lock

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

app = Flask(__name__)

GPIO.setmode(GPIO.BCM)

# Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
   23 : {'name' : 'GPIO 23', 'state' : GPIO.LOW},
   24 : {'name' : 'GPIO 24', 'state' : GPIO.LOW}
   }

buttons = {
    10: {'name': 'GPIO 10', 'state': GPIO.LOW},
    11: {'name': 'GPIO 11', 'state': GPIO.LOW}
}

for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

#inputs
# GPIO.setwarnings(False) # Ignore warning for now
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 


door1 = Door(23, GPIO.LOW)
door2 = Door(24, GPIO.LOW)
lock1 = Lock(10,door1)
lock2 = Lock(11,door2)


@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/state')
def state():
   # For each pin, read the pin state and store it in the pins dictionary:
   for pin in pins:
      pins[pin]['state'] = GPIO.input(pin)
   # Put the pin dictionary into the template data dictionary:
   templateData = {
      'pins' : pins
      }
   # Pass the template data into the template main.html and return it to the user
   return render_template('main.html', **templateData)

def button_callback(pin):
    print("Button was pushed!")

# Register events
GPIO.add_event_detect(10,GPIO.RISING,callback=button_callback) # Setup event on pin 10 rising edge

if __name__ == '__main__':
    # Debug/Development
    # app.run(debug=True, host="0.0.0.0", port="5000")
    # Production
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
    
def exit_handler():
    GPIO.cleanup() 

atexit.register(exit_handler)
