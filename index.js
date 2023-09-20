var Gpio = require('onoff').Gpio; //require onoff to control GPIO
const express = require('express'); //require express as adding a REST override for doors

// phsical
var pushButton1 = new Gpio(17, 'in', 'both', { debounceTimeout: 20 }); //use GPIO pin 17 as input
var pushButton2 = new Gpio(18, 'in', 'both', { debounceTimeout: 20 }); //use GPIO pin 18 as input
var LEDPin = new Gpio(4, 'out'); //declare GPIO4 an output
var DOORPin1 = new Gpio(20, 'out'); //declare GPIO20 an output
var DOORPin2 = new Gpio(21, 'out'); //declare GPIO21 an output
var overrideButton = false;


// api
const app = express();
app.use(express.json());
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log("Server Listening on PORT:", PORT);
});

function getDoorStatus(doorPin) {
    stat = doorPin.readSync();
    if (stat === 0) {
        statusString = "Locked";
    } else {
        statusString = "Unlocked";
    }
    const status = {
        "Status": statusString
    };
    return status;
}
const statusRoute = function (request, response, next) {
    doorsStatus = {
        door1: getDoorStatus(DOORPin1),
        door2: getDoorStatus(DOORPin2),
    }
    response.send(doorsStatus);
    next()
};

const unlockRoute = function (request, response, next) {
    overrideButton = true;
    DOORPin1.writeSync(1);
    DOORPin2.writeSync(1);
    next();
};

const isolateRoute = function (request, response, next) {
    console.log("isolating door " + request.params.door);
    //TODO
    next();
}

app.get("/status", [statusRoute]);

app.get("/unlock", [unlockRoute, statusRoute]);

app.get("/isolate/:door", [isolateRoute, statusRoute]);

var state = 0;

const buttonWatch = function (err, valule, button) {
    console.log("in:" + value + "," + state);
    if (overrideButton) {
        if (value === 1) {
            overrideButton = false;
        }
    } else {
        if (value === 0) {
            state = 1;
        } else {
            state = 0;
        }
        // state = value == 1 ? 0 :1;
        // state = value;
        LEDPin.writeSync(state);
        DOORPin1.writeSync(state);
        DOORPin2.writeSync(state);
    }
    console.log("out:" + value + "," + state);
    console.log("end");
}
pushButton1.watch(function (err, value) { buttonWatch(err, value, pushButton1); });
pushButton2.watch(function (err, value) { buttonWatch(err, value, pushButton2); });

function unexportOnClose() { //function to run when exiting program
    LEDPin.writeSync(0); // Turn LED off
    LEDPin.unexport(); // Unexport LED GPIO to free resources
    DOORPin1.writeSync(1);
    DOORPin1.unexport();
    pushButton.unexport(); // Unexport Button GPIO to free resources
};