import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Human-Tracking", layout="centered")
st.title("Human-Tracking")

html("""
<!DOCTYPE html>
<html lang="en">
<head>
    <title>ESP32 BLE Web</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background-color: #121212; color: #e0e0e0; font-family: Arial, sans-serif; padding: 20px; }
        h3, h4 { color: #ffffff; }
        button { background: #333; color: #fff; border: 1px solid #444; padding: 10px 20px; margin: 5px; cursor: pointer; }
        button:hover { background: #444; }
        #bleState { font-weight: bold; }
        .status-connected { color: #4CAF50; }
        .status-disconnected { color: #FF5252; }
    </style>
</head>
<body>
    <h3>ESP32 BLE Web App</h3>
    <button id="connectBle">Connect to ESP32</button>
    <button id="disconnectBle">Disconnect</button>
    <p>BLE State: <span id="bleState" class="status-disconnected">Disconnected</span></p>

    <h4>Received Sensor Value:</h4>
    <p id="sensorValue">-</p>

    <h4>Control LED</h4>
    <button id="ledOn">Turn ON</button>
    <button id="ledOff">Turn OFF</button>

    <script>
        let bleDevice, bleServer, bleService, sensorChar, ledChar;
        const SERVICE_UUID = "19b10000-e8f2-537e-4f6c-d104768a1214";
        const SENSOR_UUID = "19b10001-e8f2-537e-4f6c-d104768a1214";
        const LED_UUID = "19b10002-e8f2-537e-4f6c-d104768a1214";

        async function connectBLE() {
            if (bleDevice) {
                console.log("⚠️ Already connected to BLE.");
                return;
            }

            try {
                bleDevice = await navigator.bluetooth.requestDevice({
                    filters: [{ name: "ESP32-BLE" }],
                    optionalServices: [SERVICE_UUID]
                });

                bleDevice.addEventListener("gattserverdisconnected", onDisconnected);
                bleServer = await bleDevice.gatt.connect();
                bleService = await bleServer.getPrimaryService(SERVICE_UUID);

                sensorChar = await bleService.getCharacteristic(SENSOR_UUID);
                sensorChar.addEventListener("characteristicvaluechanged", handleSensorValue);
                await sensorChar.startNotifications();

                ledChar = await bleService.getCharacteristic(LED_UUID);

                document.getElementById("bleState").textContent = "Connected";
                document.getElementById("bleState").className = "status-connected";
                console.log("✅ BLE Connected Successfully!");
            } catch (error) {
                console.error("❌ Connection Error:", error);
                alert("Failed to connect. Try again.");
            }
        }

        function handleSensorValue(event) {
            let value = new TextDecoder().decode(event.target.value);
            document.getElementById("sensorValue").textContent = value;
            console.log("📡 Sensor Value:", value);
        }

        async function sendValue(value) {
            if (!ledChar) return alert("❌ BLE Not Connected");
            try {
                await ledChar.writeValue(new TextEncoder().encode(value.toString()));
                console.log(`✅ Sent ${value} to LED`);
            } catch (error) {
                console.error("❌ Write Error:", error);
            }
        }

        function onDisconnected() {
            console.log("❌ BLE Disconnected. Attempting Reconnect...");
            document.getElementById("bleState").textContent = "Disconnected";
            document.getElementById("bleState").className = "status-disconnected";
            setTimeout(connectBLE, 2000); // Auto-reconnect after 2 sec
        }

        document.getElementById("connectBle").addEventListener("click", connectBLE);
        document.getElementById("disconnectBle").addEventListener("click", () => bleDevice?.gatt.disconnect());
        document.getElementById("ledOn").addEventListener("click", () => sendValue(1));
        document.getElementById("ledOff").addEventListener("click", () => sendValue(0));
    </script>
</body>
</html>

""", height=800)
