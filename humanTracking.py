import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Human-Tracking", layout="centered")

st.title("Human-Tracking")

# Embed your full HTML + JS here using triple quotes
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
  <p>BLE state: <strong><span id="bleState" style="color:#d13a30;">Disconnected</span></strong></p>
  <h4>Fetched Value</h4>
  <p><span id="valueContainer">NaN</span></p>
  <p>Last reading: <span id="timestamp"></span></p>
  <h4>Control GPIO 2</h4>
  <button id="onButton">ON</button>
  <button id="offButton">OFF</button>
  <p>Last value sent: <span id="valueSent"></span></p>
</body>
<script>
    const connectButton = document.getElementById('connectBleButton');
    const disconnectButton = document.getElementById('disconnectBleButton');
    const onButton = document.getElementById('onButton');
    const offButton = document.getElementById('offButton');
    const retrievedValue = document.getElementById('valueContainer');
    const latestValueSent = document.getElementById('valueSent');
    const bleStateContainer = document.getElementById('bleState');
    const timestampContainer = document.getElementById('timestamp');

    var deviceName ='ESP32';
    var bleService = '19b10000-e8f2-537e-4f6c-d104768a1214';
    var ledCharacteristic = '19b10002-e8f2-537e-4f6c-d104768a1214';
    var sensorCharacteristic= '19b10001-e8f2-537e-4f6c-d104768a1214';

    var bleServer;
    var bleServiceFound;
    var sensorCharacteristicFound;

    connectButton.addEventListener('click', (event) => {
        if (isWebBluetoothEnabled()){
            connectToDevice();
        }
    });

    disconnectButton.addEventListener('click', disconnectDevice);
    onButton.addEventListener('click', () => writeOnCharacteristic(1));
    offButton.addEventListener('click', () => writeOnCharacteristic(0));

    function isWebBluetoothEnabled() {
        if (!navigator.bluetooth) {
            bleStateContainer.innerHTML = "Web Bluetooth API is not available in this browser!";
            return false
        }
        return true
    }

    function connectToDevice(){
        navigator.bluetooth.requestDevice({
            filters: [{name: deviceName}],
            optionalServices: [bleService]
        })
        .then(device => {
            bleStateContainer.innerHTML = 'Connected to device ' + device.name;
            bleStateContainer.style.color = "#24af37";
            device.addEventListener('gattservicedisconnected', onDisconnected);
            return device.gatt.connect();
        })
        .then(gattServer =>{
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
            retrievedValue.innerHTML = decodedValue;
        })
        .catch(error => {
            console.log('Error: ', error);
        })
    }

    function onDisconnected(event){
        bleStateContainer.innerHTML = "Device disconnected";
        bleStateContainer.style.color = "#d13a30";
        connectToDevice();
    }

    function handleCharacteristicChange(event){
        const newValueReceived = new TextDecoder().decode(event.target.value);
        retrievedValue.innerHTML = newValueReceived;
        timestampContainer.innerHTML = getDateTime();
    }

    function writeOnCharacteristic(value){
        if (bleServer && bleServer.connected) {
            bleServiceFound.getCharacteristic(ledCharacteristic)
            .then(characteristic => {
                const data = new Uint8Array([value]);
                return characteristic.writeValue(data);
            })
            .then(() => {
                latestValueSent.innerHTML = value;
            })
            .catch(error => {
                console.error("Error writing to characteristic: ", error);
            });
        } else {
            window.alert("Bluetooth is not connected. Connect to BLE first!")
        }
    }

    function disconnectDevice() {
        if (bleServer && bleServer.connected) {
            if (sensorCharacteristicFound) {
                sensorCharacteristicFound.stopNotifications()
                    .then(() => bleServer.disconnect())
                    .then(() => {
                        bleStateContainer.innerHTML = "Device Disconnected";
                        bleStateContainer.style.color = "#d13a30";
                    })
                    .catch(error => {
                        console.log("An error occurred:", error);
                    });
            }
        } else {
            window.alert("Bluetooth is not connected.")
        }
    }

    function getDateTime() {
        var currentdate = new Date();
        var day = ("00" + currentdate.getDate()).slice(-2);
        var month = ("00" + (currentdate.getMonth() + 1)).slice(-2);
        var year = currentdate.getFullYear();
        var hours = ("00" + currentdate.getHours()).slice(-2);
        var minutes = ("00" + currentdate.getMinutes()).slice(-2);
        var seconds = ("00" + currentdate.getSeconds()).slice(-2);

        return day + "/" + month + "/" + year + " at " + hours + ":" + minutes + ":" + seconds;
    }
</script>
</html>
<style>
             #MainMenu {visibility: hidden;}
             footer {visibility: hidden;}
             footer:after {content:'Made with ❤️ by ADITYA PURI';visibility: visible;display: block;}
             .st-emotion-cache-cio0dv {
             padding-left: 20%;
             padding-right: 1rem;
             }
             header {visibility: hidden;}
              </style>
""", height=800)
