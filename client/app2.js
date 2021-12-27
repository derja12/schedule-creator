const halfHourArray = [
    "800",
    "830",
    "900",
    "930",
    "1000",
    "1030",
    "1100",
    "1130",
    "1200",
    "1230",
    "1300",
    "1330",
    "1400",
    "1430",
    "1500",
    "1530",
    "1600",
    "1630",
    "1700",
    "1730",
    "1800",
    "1830",
    "1900",
    "1930",
    "2000",
    "2030",
    "2100",
    "2130"
]
const dayArray = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
]
const employeeDigitArray = [
    "d",
    "r",
    "k",
    "h",
    "l"
]
var switchObjects = {}
var SWITCH_MODE = false;
var SWITCH_MODE_AVAILABLE = false;
var SWITCH_MODE_UNAVAILABLE = true;

// ON RUN
runtimeActions();

// CREATE SWITCH DIVS
function createSwitchToggleDivs() {
    const scheduleWrapper = document.querySelector("#schedule-wrapper");

    halfHourArray.forEach(halfHourString => {
        dayArray.forEach(dayString => {
            var switchDiv = document.createElement("div");
            switchDiv.classList.add(dayString+"-column", "row-"+halfHourString, "switch-div");
            employeeDigitArray.forEach(employeeDigitChar => {
                var Switch = document.createElement("div");
                Switch.classList.add("switch-"+employeeDigitChar, "switch");
                Switch.id = "switch-"+halfHourString+"-"+dayString+"-"+employeeDigitChar;
                Switch.innerHTML = employeeDigitChar;
                switchDiv.appendChild(Switch);
                obj = {"available" : true}
                switchObjects[Switch.id] = obj;
                Switch.style.backgroundColor = "#0088BB";
            });
            scheduleWrapper.appendChild(switchDiv);
        });
    });
}



// SWITCH TOGGLE BUTTON
function applySwitchClicks() {
    var switches = document.querySelectorAll(".switch");
    document.querySelector("body").addEventListener("mousedown", function () {
        SWITCH_MODE = true;
    });
    document.querySelector("body").addEventListener("mouseup", function () {
        SWITCH_MODE = false;
    });
    switches.forEach(swich => {
        console.log("mousedown");
        swich.addEventListener("mouseover", switchClicked.bind(this, [swich]), false);
    });    
}
function switchClicked(switch_array) {
    if (SWITCH_MODE) {
        if (SWITCH_MODE_AVAILABLE) {
            switch_array[0].style.backgroundColor = "#0088BB";
            switchObjects[switch_array[0].id] = true;
        } else if (SWITCH_MODE_UNAVAILABLE) {
            switch_array[0].style.backgroundColor = "";
            switchObjects[switch_array[0].id] = false;
        }
    }
}

// MODE CLICK
function applyModeClick() {
    var modeSwitchDiv = document.querySelector("#switch-toggle");
    modeSwitchDiv.addEventListener("click", function () {
        if (SWITCH_MODE_UNAVAILABLE) {
            SWITCH_MODE_AVAILABLE = true;
            SWITCH_MODE_UNAVAILABLE = false;
            modeSwitchDiv.innerHTML = "MODE: AVAILABILITY";
        } else if (SWITCH_MODE_AVAILABLE) {
            SWITCH_MODE_AVAILABLE = false;
            SWITCH_MODE_UNAVAILABLE = true;    
            modeSwitchDiv.innerHTML = "MODE: UNAVAILABILITY";
        }
    });
}

// RUNTIME ACTIONS
function runtimeActions() {
    createSwitchToggleDivs();
    applySwitchClicks();
    applyModeClick();
}