# Архітектура системи

MQTT: емулятор метеостанції -> Mosquitto -> OpenHAB Thing -> Items.
HTTP/REST: Python API на http://127.0.0.1:8090.
BLE: програмна емуляція температурного сенсора, не фізичний Bluetooth-пристрій.
