import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Human-Tracking", layout="centered")

st.title("Human-Tracking")

html(f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Graphical BLE Data Display</title>
  <style>
    html, body {{
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      background-color: #1e1e1e;
      color: white;
      font-family: Arial, sans-serif;
    }}
    #appContainer {{
      display: flex;
      flex-direction: column;
      height: 100vh;
      width: 100vw;
    }}
    #canvasContainer {{
      flex-grow: 1;
    }}
    canvas {{
      width: 100vw;
      height: 100vh;
      background: #2c2c2c;
      display: block;
    }}
    #controls {{
      position: absolute;
      top: 10px;
      left: 10px;
      background-color: rgba(0, 0, 0, 0.7);
      padding: 10px;
      border-radius: 8px;
      z-index: 10;
    }}
    button {{
      background-color: #1f1f1f;
      color: #ffffff;
      border: 1px solid #444;
      padding: 10px 20px;
      margin: 5px;
      border-radius: 6px;
      cursor: pointer;
      transition: background 0.3s ease;
    }}
    button:hover {{
      background-color: #333333;
    }}
    .status-connected {{ color: #66bb6a; }}
    .status-disconnected {{ color: #ef5350; }}
    .value-label {{ color: #03dac6; margin-right: 5px; }}
    .switch {{
      position: relative;
      display: inline-block;
      width: 60px;
      height: 34px;
    }}
    .switch input {{
      opacity: 0;
      width: 0;
      height: 0;
    }}
    .slider {{
      position: absolute;
      cursor: pointer;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: #ccc;
      transition: .4s;
    }}
    .slider:before {{
      position: absolute;
      content: "";
      height: 26px;
      width: 26px;
      left: 4px;
      bottom: 4px;
      background-color: white;
      transition: .4s;
    }}
    input:checked + .slider {{
      background-color: #2196F3;
    }}
    input:checked + .slider:before {{
      transform: translateX(26px);
    }}
    .slider.round {{
      border-radius: 34px;
    }}
    .slider.round:before {{
      border-radius: 50%;
    }}
  </style>
</head>
<body>
  <div id="appContainer">
    <canvas id="trackingCanvas"></canvas>
    <div id="controls">
      <button id="connectBleButton">Connect to BLE Device</button>
      <button id="disconnectBleButton">Disconnect</button>
      <label class="switch">
        <input type="checkbox" id="ledToggle">
        <span class="slider round"></span>
      </label>
      <p>Last value sent: <span id="valueSent"></span></p>
      <div>
        <span>BLE state: <strong><span id="bleState" class="status-disconnected">Disconnected</span></strong></span><br>
        <span><span class="value-label">X:</span><span id="valX">NaN</span></span>
        <span><span class="value-label">Y:</span><span id="valY">NaN</span></span>
        <span><span class="value-label">Speed:</span><span id="valSpeed">NaN</span></span>
        <span><span class="value-label">Distance:</span><span id="valDistance">NaN</span></span>
        <span><span class="value-label">Angle:</span><span id="valAngle">NaN°</span></span>
        <span><span class="value-label">Last Reading:</span><span id="valTime">--:--:--</span></span>
      </div>
    </div>
  </div>
  <script>
    const canvas = document.getElementById('trackingCanvas');
    const ctx = canvas.getContext('2d');
    const valX = document.getElementById('valX');
    const valY = document.getElementById('valY');
    const valSpeed = document.getElementById('valSpeed');
    console.log(valSpeed);
    const valDistance = document.getElementById('valDistance');
    const valAngle = document.getElementById('valAngle');
    const valTime = document.getElementById('valTime');
    const bleStateContainer = document.getElementById('bleState');
    const connectButton = document.getElementById('connectBleButton');
    const disconnectButton = document.getElementById('disconnectBleButton');
    const ledToggle = document.getElementById('ledToggle');
    const valueSent = document.getElementById('valueSent');

    let previousPoint = null;
    let bleDevice, bleServer, bleService, sensorCharacteristic, ledCharacteristic;
    
    const deviceName = 'HUMAN_TRACKING🧑';
    const bleServiceUUID = '19b10000-e8f2-537e-4f6c-d104768a1214';
    const sensorCharacteristicUUID = '19b10001-e8f2-537e-4f6c-d104768a1214';
    const ledCharacteristicUUID = '19b10002-e8f2-537e-4f6c-d104768a1214'; // optional LED control

    function resizeCanvas() {{
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }}

    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    function drawPoint(x, y, color = '#03dac6', radius = 5) {{
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();
    }}

    function drawSensorOrigin() {{
      const originSize = 10;
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      ctx.fillStyle = 'yellow';
      ctx.fillRect(centerX - originSize/2, centerY - originSize/2, originSize, originSize);
    }}

    function drawCurrentAndPrevious(newX, newY) {{
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      drawSensorOrigin();
      if (previousPoint) {{
        drawPoint(previousPoint.x, previousPoint.y, '#888');
      }}
      drawPoint(newX, newY);
    }}

    async function connectToDevice() {{
      try {{
        bleDevice = await navigator.bluetooth.requestDevice({{
          filters: [{{ name: deviceName }}],
          optionalServices: [bleServiceUUID]
        }});

        bleDevice.addEventListener('gattserverdisconnected', onDisconnected);
        bleServer = await bleDevice.gatt.connect();
        bleService = await bleServer.getPrimaryService(bleServiceUUID);
        sensorCharacteristic = await bleService.getCharacteristic(sensorCharacteristicUUID);
        ledCharacteristic = await bleService.getCharacteristic(ledCharacteristicUUID).catch(() => null); // optional
        sensorCharacteristic.addEventListener('characteristicvaluechanged', handleData);
        await sensorCharacteristic.startNotifications();

        bleStateContainer.textContent = 'Connected';
        bleStateContainer.classList.add('status-connected');
        bleStateContainer.classList.remove('status-disconnected');

      }} catch (error) {{
        console.error('Connection Error:', error);
        alert("Failed to connect: " + error.message);
      }}
    }}

    function onDisconnected() {{
      bleStateContainer.textContent = "Disconnected";
      bleStateContainer.classList.add('status-disconnected');
      bleStateContainer.classList.remove('status-connected');
    }}

    async function disconnectDevice() {{
      if (bleDevice && bleDevice.gatt.connected) {{
        bleDevice.gatt.disconnect();
        onDisconnected();
      }}
    }}

    async function handleData(event) {{
      const buffer = event.target.value.buffer;
      const dataView = new DataView(buffer);

      const x = dataView.getInt32(0, true);
      const y = dataView.getInt32(4, true);
      const distance = Math.sqrt(x*x + y*y);
      const angle = Math.atan2(y, x) * (180 / Math.PI);

      const scaledX = canvas.width / 2 + x;
      const scaledY = canvas.height / 2 - y;

      drawCurrentAndPrevious(scaledX, scaledY);
      previousPoint = {{ x: scaledX, y: scaledY }};

      valX.textContent = x;
      valY.textContent = y;
      valDistance.textContent = distance.toFixed(2);
      valAngle.textContent = angle.toFixed(2) + "°";
      valTime.textContent = new Date().toLocaleTimeString();
    }}

    connectButton.addEventListener('click', connectToDevice);
    disconnectButton.addEventListener('click', disconnectDevice);

    async function sendLedCommand(value) {{
      if (ledCharacteristic) {{
        const buffer = new Uint8Array([value]);
        await ledCharacteristic.writeValue(buffer);
        valueSent.textContent = value === 1 ? "ON" : "OFF";
      }}
    }}

    ledToggle.addEventListener('change', () => {{
      sendLedCommand(ledToggle.checked ? 1 : 0);
    }});
  </script>
</body>
</html>
""", height=800)

