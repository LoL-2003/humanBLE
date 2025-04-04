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
</head>
<body>
  <h3>ESP32 Web BLE Application</h3>
  <button id="connectBleButton">Connect to BLE Device</button>
  <button id="disconnectBleButton">Disconnect BLE Device</button>
  <p>BLE state: <strong><span id="bleState">Disconnected</span></strong></p>

  <h4>Fetched Values</h4>
  <p>X: <span id="xValue">NaN</span></p>
  <p>Y: <span id="yValue">NaN</span></p>
  <p>Speed: <span id="speedValue">NaN</span></p>
  <p>Distance: <span id="distanceValue">NaN</span></p>
  <p>Last reading: <span id="timestamp"></span></p>

  <h4>Control GPIO 2</h4>
  <button id="onButton">ON</button>
  <button id="offButton">OFF</button>

  <script>
    let device;
    let server;
    let service;
    let sensorCharacteristic;
    
    document.getElementById('connectBleButton').addEventListener('click', async () => {
        try {
            device = await navigator.bluetooth.requestDevice({
                filters: [{ name: "ESP32" }],
                optionalServices: ['19b10000-e8f2-537e-4f6c-d104768a1214']
            });

            device.addEventListener('gattserverdisconnected', () => {
                document.getElementById('bleState').textContent = "Disconnected";
            });

            server = await device.gatt.connect();
            service = await server.getPrimaryService('19b10000-e8f2-537e-4f6c-d104768a1214');
            sensorCharacteristic = await service.getCharacteristic('19b10001-e8f2-537e-4f6c-d104768a1214');

            sensorCharacteristic.addEventListener('characteristicvaluechanged', (event) => {
                let dataView = new DataView(event.target.value.buffer);
                document.getElementById('xValue').textContent = dataView.getInt16(0, true);
                document.getElementById('yValue').textContent = dataView.getInt16(2, true);
                document.getElementById('speedValue').textContent = dataView.getInt8(4);
                document.getElementById('distanceValue').textContent = dataView.getUint16(5, true);
                document.getElementById('timestamp').textContent = new Date().toLocaleString();
            });

            await sensorCharacteristic.startNotifications();
            document.getElementById('bleState').textContent = "Connected";
        } catch (error) {
            console.error(error);
            alert("Connection failed: " + error.message);
        }
    });
  </script>
</body>
</html>

""", height=800)
