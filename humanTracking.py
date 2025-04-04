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

        h3, h4 {
            color: #ffffff;
        }

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

        button:hover {
            background-color: #333333;
        }

        #valueContainer, #timestamp, #valueSent {
            color: #90caf9;
            font-weight: bold;
        }

        #bleState {
            font-weight: bold;
        }

        .status-connected {
            color: #66bb6a;
        }

        .status-disconnected {
            color: #ef5350;
        }

        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        footer:after {
            content: 'Made with ❤️ by ADITYA PURI';
            visibility: visible;
            display: block;
            color: #888;
            text-align: center;
            padding-top: 10px;
        }

        .st-emotion-cache-cio0dv {
            padding-left: 20%;
            padding-right: 1rem;
        }
    </style>
</head>
<body>
  <h3>ESP32 Web BLE Application</h3>
  <button id="connectBleButton">Connect to BLE Device</button>
  <button id="disconnectBleButton">Disconnect BLE Device</button>
  <p>BLE state: <strong><span id="bleState" class="status-disconnected">Disconnected</span></strong></p>
  <h4>Fetched Value</h4>
  <p><span id="valueContainer">NaN</span></p>
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
    const retrievedValue = document.getElementById('valueContainer');
    const latestValueSent = document.getElementById('valueSent');
    const bleStateContainer = document.getElementById('bleState');
    const timestampContainer = document.getElementById('timestamp');

    const deviceName = 'ESP32';
    const bleService = '19b10000-e8f2-537e-4f6c-d104768a1214';
    const ledCharacteristic = '19b10002-e8f2-537e-4f6c-d104768a1214';
    const sensorCharacteristic = '19b10001-e8f2-537e-4f6c-d104768a1214';

    let bleServer = null;
    let bleServiceFound = null;
    let sensorCharacteristicFound = null;

    connectButton.addEventListener('click', () => {
        if (isWebBluetoothEnabled()) {
            connectToDevice();
        }
    });

    disconnectButton.addEventListener('click', disconnectDevice);
    onButton.addEventListener('click', () => writeOnCharacteristic(1));
    offButton.addEventListener('click', () => writeOnCharacteristic(0));

    function isWebBluetoothEnabled() {
        if (!navigator.bluetooth) {
            bleStateContainer.textContent = "Web Bluetooth API is not available in this browser!";
            return false;
        }
        return true;
    }

    function connectToDevice() {
        navigator.bluetooth.requestDevice({
            filters: [{ name: deviceName }],
            optionalServices: [bleService]
        })
        .then(device => {
            bleStateContainer.textContent = 'Connected to device ' + device.name;
            bleStateContainer.classList.remove('status-disconnected');
            bleStateContainer.classList.add('status-connected');
            device.addEventListener('gattserverdisconnected', onDisconnected);
            return device.gatt.connect();
        })
        .then(gattServer => {
            bleServer = gattServer;
            return bleServer.getPrimaryService(bleService);
        })
        .then(service => {
            bleServiceFound = service;
            return service.getCharacteristic(sensorCharacteristic);
        })
        .then(characteristic => {
            sensorCharacteristicFound = characteristic;
            characteristic.addEventListener('characteristicvaluechanged', handleCharacteristicChange);
            characteristic.startNotifications();
            return characteristic.readValue();
        })
        .then(value => {
            const decodedValue = new TextDecoder().decode(value);
            retrievedValue.textContent = decodedValue;
        })
        .catch(error => {
            console.error('Error:', error);
            bleStateContainer.textContent = 'Connection error: ' + error.message;
        });
    }

    function onDisconnected(event) {
        bleStateContainer.textContent = "Device disconnected";
        bleStateContainer.classList.remove('status-connected');
        bleStateContainer.classList.add('status-disconnected');
    }

    function handleCharacteristicChange(event) {
        const newValueReceived = new TextDecoder().decode(event.target.value);
        retrievedValue.textContent = newValueReceived;
        timestampContainer.textContent = getDateTime();
    }

    function writeOnCharacteristic(value) {
        if (bleServer && bleServer.connected) {
            bleServiceFound.getCharacteristic(ledCharacteristic)
                .then(characteristic => {
                    const data = new Uint8Array([value]);
                    return characteristic.writeValue(data);
                })
                .then(() => {
                    latestValueSent.textContent = value;
                })
                .catch(error => {
                    console.error("Error writing to characteristic:", error);
                    alert("Write error: " + error.message);
                });
        } else {
            alert("Bluetooth is not connected. Connect to BLE first!");
        }
    }

    function disconnectDevice() {
        if (bleServer && bleServer.connected) {
            if (sensorCharacteristicFound) {
                sensorCharacteristicFound.stopNotifications()
                    .then(() => bleServer.disconnect())
                    .then(() => {
                        bleStateContainer.textContent = "Device Disconnected";
                        bleStateContainer.classList.remove('status-connected');
                        bleStateContainer.classList.add('status-disconnected');
                    })
                    .catch(error => {
                        console.error("Error during disconnect:", error);
                        alert("Disconnect error: " + error.message);
                    });
            }
        } else {
            alert("Bluetooth is not connected.");
        }
    }

    function getDateTime() {
        const currentdate = new Date();
        const day = ("00" + currentdate.getDate()).slice(-2);
        const month = ("00" + (currentdate.getMonth() + 1)).slice(-2);
        const year = currentdate.getFullYear();
        const hours = ("00" + currentdate.getHours()).slice(-2);
        const minutes = ("00" + currentdate.getMinutes()).slice(-2);
        const seconds = ("00" + currentdate.getSeconds()).slice(-2);
        return `${day}/${month}/${year} at ${hours}:${minutes}:${seconds}`;
    }
  </script>
</body>
</html>
""", height=800)
