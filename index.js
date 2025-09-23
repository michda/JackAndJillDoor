var Gpio = require('onoff').Gpio; //require onoff to control GPIO
const express = require('express'); //require express as adding a REST override for doors

// phsical
var pushButton1 = new Gpio(526, 'in', 'falling'); //use GPIO pin 14 as input
var pushButton2 = new Gpio(527, 'in', 'falling'); //use GPIO pin 15 as input
var DOORPin1 = new Gpio(531, 'out'); //declare GPIO19 an output
var DOORPin2 = new Gpio(525, 'out'); //declare GPIO26 an output
var overrideButton = false;

// initialize to open
DOORPin1.writeSync(1);
DOORPin2.writeSync(1);

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

const lockRoute = function (request, response, next) {
    overrideButton = true;
    DOORPin1.writeSync(1);
    DOORPin2.writeSync(1);
    next();
};

const unlockRoute = function (request, response, next) {
    overrideButton = true;
    DOORPin1.writeSync(0);
    DOORPin2.writeSync(0);
    next();
};

const isolateRoute = function (request, response, next) {
    console.log("isolating door " + request.params.door);
    //TODO
    next();
}

app.get("/status", [statusRoute]);
app.get("/lock", [lockRoute, statusRoute]);
app.get("/unlock", [unlockRoute, statusRoute]);

app.get("/isolate/:door", [isolateRoute, statusRoute]);

var state = 0;

const buttonWatch = function (err, value, button) {
    console.log("in:" + value + "," + state);
    if (overrideButton) {
        if (value === 1) {
            overrideButton = false;
        }
    } else {
        if (state === 0) {
            state = 1;
        } else {
            state = 0;
        }
        // state = value == 1 ? 0 : 1;
        // state = value;
        // LEDPin.writeSync(state);
        DOORPin1.writeSync(state);
        DOORPin2.writeSync(state);
    }
    console.log("out:" + value + "," + state);
    console.log("end");
}
pushButton1.watch(function (err, value) { buttonWatch(err, state, pushButton1); });
pushButton2.watch(function (err, value) { buttonWatch(err, state, pushButton2); });

function unexportOnClose() { //function to run when exiting program
    // LEDPin.writeSync(0); // Turn LED off
    // LEDPin.unexport(); // Unexport LED GPIO to free resources
    DOORPin1.writeSync(1);
    DOORPin2.writeSync(1);
    DOORPin1.unexport();
    DOORPin2.unexport();
    pushButton1.unexport(); // Unexport Button GPIO to free resources
    pushButton2.unexport(); // Unexport Button GPIO to free resources
};

