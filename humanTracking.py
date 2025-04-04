let bleDevice;
let sensorCharacteristic;
const SERVICE_UUID = "19b10000-e8f2-537e-4f6c-d104768a1214";
const SENSOR_CHARACTERISTIC_UUID = "19b10001-e8f2-537e-4f6c-d104768a1214";
const LED_CHARACTERISTIC_UUID = "19b10002-e8f2-537e-4f6c-d104768a1214";

async function connectToBLE() {
    try {
        bleDevice = await navigator.bluetooth.requestDevice({
            acceptAllDevices: true,
            optionalServices: [SERVICE_UUID]
        });

        const server = await bleDevice.gatt.connect();
        const service = await server.getPrimaryService(SERVICE_UUID);
        sensorCharacteristic = await service.getCharacteristic(SENSOR_CHARACTERISTIC_UUID);
        await sensorCharacteristic.startNotifications();
        sensorCharacteristic.addEventListener('characteristicvaluechanged', handleData);

        document.getElementById("bleState").innerText = "Connected to ESP32";
        document.getElementById("bleState").style.color = "green";
    } catch (error) {
        console.error("Connection failed: ", error);
    }
}

async function disconnectBLE() {
    if (bleDevice) {
        await bleDevice.gatt.disconnect();
        document.getElementById("bleState").innerText = "Disconnected";
        document.getElementById("bleState").style.color = "red";
        console.log("Disconnected");
    }
}

async function handleData(event) {
    const buffer = event.target.value.buffer;
    const dataView = new DataView(buffer);

    let rawData = new Uint8Array(buffer);
    console.log("🔹 Raw Data Received:", rawData);

    let x = dataView.getInt16(0, true);
    let y = dataView.getInt16(2, true);
    let speed = dataView.getInt8(4);
    let distance = dataView.getUint16(5, true);

    console.log(`Decoded Data: X=${x}, Y=${y}, Speed=${speed}, Distance=${distance}`);

    document.getElementById("xValueContainer").textContent = x;
    document.getElementById("yValueContainer").textContent = y;
    document.getElementById("speedContainer").textContent = speed;
    document.getElementById("distanceContainer").textContent = distance;
    document.getElementById("timestampContainer").textContent = new Date().toLocaleString();
}

async function toggleLED(state) {
    try {
        const service = await bleDevice.gatt.getPrimaryService(SERVICE_UUID);
        const ledCharacteristic = await service.getCharacteristic(LED_CHARACTERISTIC_UUID);
        let data = new Uint8Array([state]);
        await ledCharacteristic.writeValue(data);
        console.log(`LED ${state ? "ON" : "OFF"}`);
    } catch (error) {
        console.error("Failed to toggle LED: ", error);
    }
}
