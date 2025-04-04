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
        .status-connected { color: #66bb6a; }
        .status-disconnected { color: #ef5350; }
    </style>
</head>
<body>
  <h3>ESP32 Web BLE Application</h3>
  <button id="connectBleButton">Connect to BLE Device</button>
  <button id="disconnectBleButton">Disconnect BLE Device</button>
  <p>BLE state: <strong><span id="bleState" class="status-disconnected">Disconnected</span></strong></p>
  
  <h4>Fetched Sensor Data</h4>
  <p>X: <span id="xValue">NaN</span></p>
  <p>Y: <span id="yValue">NaN</span></p>
  <p>Speed: <span id="speedValue">NaN</span></p>
  <p>Distance: <span id="distanceValue">NaN</span></p>
  
  <script>
    let bleDevice, bleServer, bleService, sensorCharacteristic;
    const serviceUUID = '19b10000-e8f2-537e-4f6c-d104768a1214';
    const sensorUUID = '19b10001-e8f2-537e-4f6c-d104768a1214';

    document.getElementById("connectBleButton").addEventListener("click", async () => {
        try {
            bleDevice = await navigator.bluetooth.requestDevice({ filters: [{ name: 'ESP32' }], optionalServices: [serviceUUID] });
            bleServer = await bleDevice.gatt.connect();
            bleService = await bleServer.getPrimaryService(serviceUUID);
            sensorCharacteristic = await bleService.getCharacteristic(sensorUUID);

            sensorCharacteristic.addEventListener('characteristicvaluechanged', handleData);
            await sensorCharacteristic.startNotifications();
            document.getElementById("bleState").textContent = "Connected";
            document.getElementById("bleState").className = "status-connected";
        } catch (error) { console.error("Connection failed", error); }
    });

    function handleData(event) {
        const buffer = event.target.value.buffer;
        const dataView = new DataView(buffer);
        document.getElementById("xValue").textContent = dataView.getInt32(0, true);
        document.getElementById("yValue").textContent = dataView.getInt32(4, true);
        document.getElementById("speedValue").textContent = dataView.getUint8(8);
        document.getElementById("distanceValue").textContent = dataView.getUint16(9, true);
    }
  </script>
</body>
</html>
""", height=800)
