#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

BLEServer* pServer = NULL;
BLECharacteristic* pSensorCharacteristic = NULL;
BLECharacteristic* pLedCharacteristic = NULL;
bool deviceConnected = false;
bool oldDeviceConnected = false;

// Sensor data structure
struct SensorData {
    int32_t x;
    int32_t y;
    uint8_t speed;
    uint16_t distance;
};

SensorData getRandomSensorData() {
    SensorData data;
    data.x = random(-60, 60);
    data.y = random(-30, 30);
    data.speed = random(1, 21); // Speed between 1-20
    data.distance = sqrt(data.x * data.x + data.y * data.y);
    return data;
}

const int ledPin = 2;

// BLE UUIDs
#define SERVICE_UUID                  "19b10000-e8f2-537e-4f6c-d104768a1214"
#define SENSOR_CHARACTERISTIC_UUID   "19b10001-e8f2-537e-4f6c-d104768a1214"
#define LED_CHARACTERISTIC_UUID      "19b10002-e8f2-537e-4f6c-d104768a1214"

class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
        deviceConnected = true;
    }

    void onDisconnect(BLEServer* pServer) {
        deviceConnected = false;
    }
};

class MyCharacteristicCallbacks : public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic* pCharacteristic) {
        std::string rawValue = pCharacteristic->getValue();
        if (rawValue.length() > 0) {
            uint8_t receivedByte = rawValue[0];
            Serial.print("Received LED command: ");
            Serial.println(receivedByte);

            if (receivedByte == 1) {
                digitalWrite(ledPin, HIGH);
                Serial.println("LED ON");
            } else if (receivedByte == 0) {
                digitalWrite(ledPin, LOW);
                Serial.println("LED OFF");
            } else {
                Serial.println("Invalid value for LED!");
            }
        }
    }
};

void setup() {
    Serial.begin(115200);
    pinMode(ledPin, OUTPUT);
    digitalWrite(ledPin, LOW);

    BLEDevice::init("HUMAN_TRACKING🧑");
    pServer = BLEDevice::createServer();
    pServer->setCallbacks(new MyServerCallbacks());

    BLEService* pService = pServer->createService(SERVICE_UUID);

    // Sensor characteristic
    pSensorCharacteristic = pService->createCharacteristic(
        SENSOR_CHARACTERISTIC_UUID,
        BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
    );
    pSensorCharacteristic->addDescriptor(new BLE2902());

    // LED control characteristic
    pLedCharacteristic = pService->createCharacteristic(
        LED_CHARACTERISTIC_UUID,
        BLECharacteristic::PROPERTY_WRITE
    );
    pLedCharacteristic->setCallbacks(new MyCharacteristicCallbacks());
    pLedCharacteristic->addDescriptor(new BLE2902());

    pService->start();

    // Start BLE advertising
    BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(SERVICE_UUID);
    pAdvertising->setScanResponse(false);
    pAdvertising->setMinPreferred(0x06); // Recommended settings
    pAdvertising->setMinPreferred(0x12);
    BLEDevice::startAdvertising();

    Serial.println("Waiting for BLE client...");
}

void loop() {
    // Only send data if connected
    if (deviceConnected) {
        SensorData sensorData = getRandomSensorData();
        pSensorCharacteristic->setValue((uint8_t*)&sensorData, sizeof(SensorData));
        pSensorCharacteristic->notify();

        Serial.print("Notify -> X: ");
        Serial.print(sensorData.x);
        Serial.print(", Y: ");
        Serial.print(sensorData.y);
        Serial.print(", Speed: ");
        Serial.print(sensorData.speed);
        Serial.print(", Distance: ");
        Serial.println(sensorData.distance);

        delay(500);
    }

    // Handle disconnect -> reconnect logic
    if (!deviceConnected && oldDeviceConnected) {
        delay(500); // Short delay before restarting advertising
        BLEDevice::startAdvertising();
        Serial.println("Client disconnected. Restarting advertising...");
        oldDeviceConnected = false;
    }

    // Handle connect transition
    if (deviceConnected && !oldDeviceConnected) {
        Serial.println("Client connected!");
        oldDeviceConnected = true;
    }
}
