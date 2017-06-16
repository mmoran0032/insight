
var Chart = require('chart.js');

var ctx = document.getElementById("mainLineChart").getContext("2d");
var mainLineChart = new Chart(ctx, {
    type: "line",
    data: {
        label = ''
        data = 
    },
    options: {
        steppedLine: true
    }
});

var lastIndex = "";
function updateStation() {
    var e = document.getElementById("station-select");
    if (e.selectedIndex >= 0) {
        document.getElementById("station-name").text =
            e.options[e.selectedIndex].value;
        lastIndex = e.selectedIndex;
    } else {
        lastIndex = "";
    }
}
document.getElementById("station-select").addEventListener("click", updateStation);
