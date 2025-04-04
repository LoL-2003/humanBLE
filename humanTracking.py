import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Bluetooth Connect", layout="centered")

st.title("🔵 Bluetooth Device Connector")

st.markdown("""
Click the button below to scan for nearby Bluetooth devices using your browser's Web Bluetooth API.
""")

html(
    """
    <button onclick="connectBluetooth()" style="padding: 10px 20px; font-size: 16px;">🔗 Connect Bluetooth Device</button>
    <p id="status" style="margin-top: 20px; font-size: 18px;"></p>

    <script>
    async function connectBluetooth() {
        try {
            const device = await navigator.bluetooth.requestDevice({
                acceptAllDevices: true
            });
            document.getElementById('status').innerText = '✅ Connected to: ' + device.name;
        } catch (error) {
            document.getElementById('status').innerText = '❌ Error: ' + error;
        }
    }
    </script>
    """,
    height=300
)
