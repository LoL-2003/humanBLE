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
        body { background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; }
        h3, h4 { color: #ffffff; }
        button { background-color: #1f1f1f; color: #ffffff; border: 1px solid #444; padding: 10px 20px; margin: 5px; border-radius: 6px; cursor: pointer; transition: background 0.3s ease; }
        button:hover { background-color: #333333; }
        #valueContainer, #timestamp, #valueSent { color: #90caf9; font-weight: bold; }
        #bleState { font-weight: bold; }
        .status-connected { color: #66bb6a; }
        .status-disconnected { color: #ef5350; }
        footer:after { content: 'Made with ❤️ by ADITYA PURI'; visibility: visible; display: block; color: #888; text-align: center; padding-top: 10px; }
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
    const deviceName = 'ESP32';
    const bleService = '19b10000-e8f2-537e-4f6c-d104768a1214';
    const ledCharacteristic = '19b10002-e8f2-537e-4f6c-d104768a1214';
    const sensorCharacteristic = '19b10001-e8f2-537e-4f6c-d104768a1214';

    let bleServer = null;
    let bleServiceFound = null;
    let sensorCharacteristicFound = null;

    document.getElementById('connectBleButton').addEventListener('click', () => { if (isWebBluetoothEnabled()) connectToDevice(); });
    document.getElementById('disconnectBleButton').addEventListener('click', disconnectDevice);
    document.getElementById('onButton').addEventListener('click', () => writeOnCharacteristic(1));
    document.getElementById('offButton').addEventListener('click', () => writeOnCharacteristic(0));

    function isWebBluetoothEnabled() {
        return navigator.bluetooth ? true : (alert("Web Bluetooth API is not available!"), false);
    }

    function connectToDevice() {
        navigator.bluetooth.requestDevice({ filters: [{ name: deviceName }], optionalServices: [bleService] })
        .then(device => device.gatt.connect())
        .then(gattServer => (bleServer = gattServer, bleServer.getPrimaryService(bleService)))
        .then(service => (bleServiceFound = service, service.getCharacteristic(sensorCharacteristic)))
        .then(characteristic => {
            sensorCharacteristicFound = characteristic;
            characteristic.addEventListener('characteristicvaluechanged', handleCharacteristicChange);
            return characteristic.startNotifications();
        })
        .catch(error => console.error('Error:', error));
    }

    function handleCharacteristicChange(event) {
        let valueReceived = new TextDecoder().decode(event.target.value);
        document.getElementById('valueContainer').textContent = valueReceived;
        document.getElementById('timestamp').textContent = new Date().toLocaleTimeString();
    }

    function writeOnCharacteristic(value) {
        if (bleServer && bleServer.connected) {
            bleServiceFound.getCharacteristic(ledCharacteristic)
                .then(characteristic => characteristic.writeValue(new TextEncoder().encode(value.toString())))
                .then(() => document.getElementById('valueSent').textContent = value)
                .catch(error => alert("Write error: " + error.message));
        } else alert("Bluetooth is not connected. Connect to BLE first!");
    }

    function disconnectDevice() {
        if (bleServer && bleServer.connected) {
            sensorCharacteristicFound.stopNotifications().then(() => bleServer.disconnect());
        } else alert("Bluetooth is not connected.");
    }
  </script>
</body>
</html>
""", height=800)
