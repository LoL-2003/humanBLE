import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Human-Tracking", layout="centered")

st.title("Human-Tracking")

html("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP32 BLE Sensor</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 20px; }
        .container { display: inline-block; text-align: left; margin-top: 20px; }
        h2 { color: #007bff; }
        .value { font-size: 20px; font-weight: bold; }
        #status { color: red; font-weight: bold; }
        button { padding: 10px; font-size: 16px; margin: 10px; cursor: pointer; }
    </style>
</head>
<body>
    <h2>ESP32 BLE Sensor Data</h2>
    <button onclick="connectToBLE()">Connect to ESP32</button>
    <p id="status">Disconnected</p>

    <div class="container">
        <p><b>X:</b> <span id="xValue" class="value">--</span></p>
        <p><b>Y:</b> <span id="yValue" class="value">--</span></p>
        <p><b>Speed:</b> <span id="speedValue" class="value">--</span></p>
        <p><b>Distance:</b> <span id="distanceValue" class="value">--</span></p>
        <p><b>Last Updated:</b> <span id="timestamp" class="value">--</span></p>
    </div>

    <button onclick="toggleLED(1)">Turn LED ON</button>
    <button onclick="toggleLED(0)">Turn LED OFF</button>

    <script>
        let device, sensorCharacteristic, ledCharacteristic;
        const SERVICE_UUID = "19b10000-e8f2-537e-4f6c-d104768a1214";
        const SENSOR_CHAR_UUID = "19b10001-e8f2-537e-4f6c-d104768a1214";
        const LED_CHAR_UUID = "19b10002-e8f2-537e-4f6c-d104768a1214";

        async function connectToBLE() {
            try {
                console.log("Requesting BLE device...");
                device = await navigator.bluetooth.requestDevice({
                    filters: [{ services: [SERVICE_UUID] }],
                    optionalServices: [SERVICE_UUID]
                });

                console.log("Connecting to GATT server...");
                const server = await device.gatt.connect();
                document.getElementById('status').textContent = "Connected ✅";
                document.getElementById('status').style.color = "green";

                console.log("Getting service...");
                const service = await server.getPrimaryService(SERVICE_UUID);

                console.log("Getting characteristics...");
                sensorCharacteristic = await service.getCharacteristic(SENSOR_CHAR_UUID);
                ledCharacteristic = await service.getCharacteristic(LED_CHAR_UUID);

                // Enable notifications for sensor data
                await sensorCharacteristic.startNotifications();
                sensorCharacteristic.addEventListener('characteristicvaluechanged', handleData);
                console.log("Notifications started.");
            } catch (error) {
                console.error("BLE Error:", error);
                document.getElementById('status').textContent = "Connection Failed ❌";
                document.getElementById('status').style.color = "red";
            }
        }

        async function handleData(event) {
            const buffer = event.target.value.buffer;
            const dataView = new DataView(buffer);
            const rawData = new Uint8Array(buffer);

            console.log("Raw Data Received:", rawData);

            let x = dataView.getInt32(0, true);  // 4 bytes (Little-Endian)
            let y = dataView.getInt32(4, true);  // 4 bytes (Little-Endian)
            let speed = dataView.getUint8(8);    // 1 byte
            let distance = dataView.getUint16(9, true);  // 2 bytes (Little-Endian)

            console.log(`Extracted Values: X=${x}, Y=${y}, Speed=${speed}, Distance=${distance}`);

            document.getElementById('xValue').textContent = x;
            document.getElementById('yValue').textContent = y;
            document.getElementById('speedValue').textContent = speed;
            document.getElementById('distanceValue').textContent = distance;
            document.getElementById('timestamp').textContent = new Date().toLocaleString();
        }

        async function toggleLED(value) {
            if (!ledCharacteristic) {
                alert("Not connected to ESP32!");
                return;
            }

            try {
                let ledState = new Uint8Array([value]);
                await ledCharacteristic.writeValue(ledState);
                console.log(`LED ${value ? "ON" : "OFF"} command sent.`);
            } catch (error) {
                console.error("Error writing to LED characteristic:", error);
            }
        }
    </script>
</body>
</html>

""", height=800)
