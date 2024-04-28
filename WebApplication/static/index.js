// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    // Get API Key in Firebase Project Settings
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// เรียกใช้ Firebase database
var database = firebase.database();
var dataRef = database.ref();

// Function to convert temperature to color
function temperature_to_color(temperature) {
    if (temperature < 24.99) {
        return "#3b4cc0";
    } else if (temperature < 25.51) {
        return "#506bda";
    } else if (temperature < 25.99) {
        return "#6788ee";
    } else if (temperature < 26.51) {
        return "#80a3fa";
    } else if (temperature < 26.99) {
        return "#9abbff";
    } else if (temperature < 27.51) {
        return "#b2ccfb";
    } else if (temperature < 27.99) {
        return "#c9d7f0";
    } else if (temperature < 28.55) {
        return "#dddcdc";
    } else if (temperature < 28.99) {
        return "#edd1c2";
    } else if (temperature < 29.55) {
        return "#f6bfa6";
    } else if (temperature < 29.99) {
        return "#f7a889";
    } else if (temperature < 30.55) {
        return "#f08a6c";
    } else if (temperature < 30.99) {
        return "#e26952";
    } else if (temperature < 31.55) {
        return "#cd423b";
    } else if (temperature < 31.99) {
        return "#b40426";
    }
}

// Function to create DataFrame-like structure
function createDataFrame(values) {
    var combinedData = {};
    values.forEach(function (value, i) {
        var key = i.toString();
        combinedData[key] = value;
    });

    // Assuming combined_data is an object in JavaScript similar to a dictionary in Python
    let allFloatNumber = Object.values(combinedData).flatMap(sublist => sublist);

    return [allFloatNumber];
}

// Function to update heatmap canvas
function updateHeatmapCanvas(intValues) {
    var canvas = document.getElementById("heatmapCanvas");
    var context = canvas.getContext("2d");

    var rectWidth = canvas.width / 32; // Assuming 32 columns in the frame
    var rectHeight = canvas.height / 24; // Assuming 24 rows in the frame

    for (var i = 0; i < 24; i++) {
        for (var j = 0; j < 32; j++) {
            var temperature = intValues[i * 32 + j];
            var color = temperature_to_color(temperature);
            context.fillStyle = color;
            context.fillRect(j * rectWidth, i * rectHeight, rectWidth, rectHeight);
        }
    }
}

// Function to Predict
function fetchPrediction() {
    fetch('/predict')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('showTimestamp').innerHTML = data.message.timestamp;
                if (data.message.result == '0') {
                    document.getElementById('showResults').innerHTML = 'ไม่มีผู้อาศัย';
                } else if (data.message.result == '1') {
                    document.getElementById('showResults').innerHTML = 'มีผู้อาศัยน้อยกว่าหรือเท่ากับ 3 ราย';
                } else if (data.message.result == '2') {
                    document.getElementById('showResults').innerHTML = 'มีผู้อาศัยมากกว่า 3 ราย';
                }
            } else {
                console.error('Prediction failed:', data.message);
            }
        })
        .catch(error => {
            console.error('Error fetching prediction:', error);
        });
}

var predictionCalled = 0;

dataRef.on("value", function (snapshot) {
    var data = snapshot.val();

    // Clear existing table data
    var dataTable = document.getElementById("dataTable");
    dataTable.innerHTML = "<tr><th>Key</th><th>Value</th></tr>";

    if (data && data.rawData) {
        // Display data in the table
        for (var key in data.rawData) {
            if (data.rawData.hasOwnProperty(key)) {
                var row = dataTable.insertRow();
                var keyCell = row.insertCell(0);
                var valueCell = row.insertCell(1);

                // Set the initial display property to none for cells
                keyCell.style.display = "none";
                valueCell.style.display = "none";

                keyCell.innerHTML = key;

                // Ensure that the value is a string before using split
                var value = String(data.rawData[key]);

                // Assuming the values are comma-separated in the format "value1,value2"
                var values = value.split(',');
                floatValues = values.map(function (value) {
                    return parseFloat(value.trim(), 10);
                });
                valueCell.innerHTML = floatValues.join(',');
            }
        }

        if (predictionCalled == 12) {
            updateHeatmapCanvas(floatValues);
            fetchPrediction();
            predictionCalled = 0;
        } else {
            predictionCalled += 1;
        }

    } else {
        console.log("No rawData found in Firebase.");
    }
}, function (error) {
    console.error("Error fetching data from Firebase:", error);
});

dataRef.child("logData").on("value", function (snapshot) {
    var data = snapshot.val();

    // Clear existing table data
    var dataTable = document.getElementById("logDataTable");
    dataTable.innerHTML = "<tr><th>ลำดับ</th><th>วันที่และเวลา</th><th>ผลลัพธ์การทำนาย</th></tr>";

    if (data && Object.keys(data).length > 1) { // Check if data exists and has more than 1 row
        var rowCount = 1;
        var lastKeys = Object.keys(data).slice(-4); // เลือก 4 คีย์ล่าสุด
        lastKeys.pop();
        lastKeys.reverse();
        for (var i = 0; i < lastKeys.length; i++) {
            var key = lastKeys[i];
            var row = dataTable.insertRow();
            var orderCell = row.insertCell(0);
            var datetimeCell = row.insertCell(1);
            var predictionCell = row.insertCell(2);

            orderCell.textContent = rowCount;
            datetimeCell.textContent = key;
            if (data[key] == '0') {
                predictionCell.textContent = 'ไม่มีผู้อาศัย';
            } else if (data[key] == '1') {
                predictionCell.textContent = 'มีผู้อาศัยน้อยกว่าหรือเท่ากับ 3 ราย';
            } else if (data[key] == '2') {
                predictionCell.textContent = 'มีผู้อาศัยมากกว่า 3 ราย';
            }
            rowCount++;
        }
    } else {
        // Insert "-" for all cells
        for (var i = 0; i < 1; i++) { // Insert 1 row with "-"
            var row = dataTable.insertRow();
            for (var j = 0; j < 3; j++) { // 3 cells per row
                var cell = row.insertCell(j);
                cell.textContent = "-";
            }
        }
        console.log("No logData found in Firebase.");
    }
}, function (error) {
    console.error("Error fetching logData from Firebase:", error);
});
