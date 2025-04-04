import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Human-Tracking", layout="centered")

st.title("Human-Tracking")

html("""
<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Web BLE App</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            background-color: #121212;
            color: #e0e0e0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px;
        }

        h3, h4 { color: #ffffff; }

        button {
            background-color: #1f1f1f;
            color: #ffffff;
            border: 1px solid #444;
            padding: 10px 20px;
            margin: 5px;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.3s ease;
        }

        button:hover { background-color: #333333; }

        #valueContainer, #timestamp, #valueSent {
            color: #90caf9;
            font-weight: bold;
        }

        #bleState { font-weight: bold; }

        .status-connected { color: #66bb6a; }
        .status-disconnected { color: #ef5350; }

        #MainMenu, header, footer { visibility: hidden; }
        footer:after {
            content: 'Made with ❤️ by ADITYA PURI';
            visibility: visible;
            display: block;
            color: #888;
            text-align: center;
            padding-top: 10px;
        }
    </style>
</head>
<body>
  <h3>ESP32 Web BLE Application</h3>
  <button id="connectBleButton">Connect to BLE Device</button>
  <button id="disconnectBleButton">Disconnect BLE Device</button>
  <p>BLE state: <strong><span id="bleState" class="status-disconnected">Disconnected</span></strong></p>

  <h4>Fetched Values</h4>
  <p>X: <span id="xValue">NaN</span></p>
  <p>Y: <span id="yValue">NaN</span></p>
  <p>Speed: <span id="speedValue">NaN</span></p>
  <p>Distance: <span id="distanceValue">NaN</span></p>
  <p>Last reading: <span id="timestamp"></span></p>

  <h4>Control GPIO 2</h4>
  <button id="onButton">ON</button>
  <button id="offButton">OFF</button>
  <p>Last value sent: <span id="valueSent"></span></p>

  <script>
    const connectButton = document.getElementById('connectBleButton');
    const disconnectButton = document.getElementById('disconnectBleButton');
    const onButton = document.getElementById('onButton');
    const offButton = document.getElementById('offButton');

    const xValueContainer = document.getElementById('xValue');
    const yValueContainer = document.getElementById('yValue');
    const speedContainer = document.getElementById('speedValue');
    const distanceContainer = document.getElementById('distanceValue');
    const timestampContainer = document.getElementById('timestamp');
    const latestValueSent = document.getElementById('valueSent');
    const bleStateContainer = document.getElementById('bleState');

    const deviceName = 'ESP32';
    const bleServiceUUID = '19b10000-e8f2-537e-4f6c-d104768a1214';
    const ledCharacteristicUUID = '19b10002-e8f2-537e-4f6c-d104768a1214';
    const sensorCharacteristicUUID = '19b10001-e8f2-537e-4f6c-d104768a1214';

    let bleDevice = null;
    let bleServer = null;
    let bleService = null;
    let sensorCharacteristic = null;

    connectButton.addEventListener('click', connectToDevice);
    disconnectButton.addEventListener('click', disconnectDevice);
    onButton.addEventListener('click', () => writeToCharacteristic(1));
    offButton.addEventListener('click', () => writeToCharacteristic(0));

    function isWebBluetoothEnabled() {
        if (!navigator.bluetooth) {
            alert("Web Bluetooth API is not available in this browser!");
            return false;
        }
        return true;
    }

    async function connectToDevice() {
        if (!isWebBluetoothEnabled()) return;

        try {
            bleDevice = await navigator.bluetooth.requestDevice({
                filters: [{ name: deviceName }],
                optionalServices: [bleServiceUUID]
            });

            bleDevice.addEventListener('gattserverdisconnected', onDisconnected);
            bleServer = await bleDevice.gatt.connect();

            bleService = await bleServer.getPrimaryService(bleServiceUUID);
            sensorCharacteristic = await bleService.getCharacteristic(sensorCharacteristicUUID);

            sensorCharacteristic.addEventListener('characteristicvaluechanged', handleData);
            await sensorCharacteristic.startNotifications();

            bleStateContainer.textContent = 'Connected to ' + bleDevice.name;
            bleStateContainer.classList.remove('status-disconnected');
            bleStateContainer.classList.add('status-connected');

            console.log("Connected successfully!");

        } catch (error) {
            console.error('Connection Error:', error);
            alert("Failed to connect: " + error.message);
            bleStateContainer.textContent = 'Disconnected';
        }
    }

    function onDisconnected() {
        bleStateContainer.textContent = "Device disconnected";
        bleStateContainer.classList.remove('status-connected');
        bleStateContainer.classList.add('status-disconnected');
        console.log("Device Disconnected");
    }



async function handleData(event) {
    const buffer = event.target.value.buffer;
    const dataView = new DataView(buffer);
    const rawData = new Uint8Array(buffer);

    console.log("Raw Data Received:", rawData);

    let x = dataView.getInt32(0, true);   // 4 bytes (Little-Endian)
    let y = dataView.getInt32(4, true);   // 4 bytes (Little-Endian)
    let speed = dataView.getInt8(8);      // 1 byte (Signed)

    // Try both endian formats and see which works
    let distance = dataView.getUint16(10, true);  // Little-Endian

    console.log(`Extracted Values (LE):distance_LE=${distance_LE}`);
    console.log(`Extracted Values (BE):distance_BE=${distance_BE}`);

    // Display values
    document.getElementById('xValue').textContent = x;
    document.getElementById('yValue').textContent = y;
    document.getElementById('speedValue').textContent = speed;
    document.getElementById('distanceValue').textContent = distance_BE; // Try swapping to LE if needed
    document.getElementById('timestamp').textContent = new Date().toLocaleString();
}




    async function writeToCharacteristic(value) {
        if (!bleServer || !bleServer.connected) {
            alert("Not connected to BLE device.");
            return;
        }

        try {
            const characteristic = await bleService.getCharacteristic(ledCharacteristicUUID);
            await characteristic.writeValue(new Uint8Array([value]));
            latestValueSent.textContent = value;
            console.log("Value sent:", value);
        } catch (error) {
            console.error("Write Error:", error);
            alert("Failed to send data: " + error.message);
        }
    }

    async function disconnectDevice() {
        if (!bleDevice || !bleDevice.gatt.connected) {
            alert("No device connected.");
            return;
        }

        try {
            await bleDevice.gatt.disconnect();
            bleStateContainer.textContent = "Device Disconnected";
            bleStateContainer.classList.remove('status-connected');
            bleStateContainer.classList.add('status-disconnected');
            console.log("Device disconnected successfully.");
        } catch (error) {
            console.error("Disconnect Error:", error);
            alert("Error disconnecting: " + error.message);
        }
    }
  </script>
</body>
</html>
""", height=800)
