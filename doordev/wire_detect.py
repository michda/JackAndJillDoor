try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
    
GPIO.setmode(GPIO.BOARD)
#inputs
# GPIO.setwarnings(False) # Ignore warning for now
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 

def button_callback(channel):
    print("event Button was pushed!")
    print(channel)

GPIO.add_event_detect(10,GPIO.RISING,callback=button_callback) # Setup event on pin 10 rising edge
a=1
while True: # Run forever
    if GPIO.input(10) == GPIO.HIGH:
        # print("Button was pushed!")
        a=2
    