OpenHAB Smart Home — Kitchen Automation

Навчальний проєкт з автоматизації розумного будинку на базі openHAB, Mosquitto MQTT та Python.

Мета проєкту

Створити систему моніторингу кухні та керування освітленням за допомогою сценаріїв.

Можливості

Моніторинг температури.

Моніторинг вологості.

Симуляція датчика руху.

Керування яскравістю освітлення від 0 до 100%.

Чотири сценарії освітлення:

Ранок — 80%.

День — 100%.

Вечір — 50%.

Ніч — 10%.

Передавання показників через MQTT.

Вебінтерфейс openHAB.

Технології

openHAB 4.1.0

Java 17

Eclipse Mosquitto

Python 3

paho-mqtt

Структура проєкту

openhab-smart-home/
├── config/
│   ├── openhab/
│   │   ├── kitchen.items
│   │   └── kitchen.rules
│   └── mosquitto/
│       └── mosquitto.conf.example
├── docs/
├── screenshots/
├── scripts/
│   └── sensor_simulator.py
├── requirements.txt
├── .gitignore
└── README.md

Запуск симулятора

Встанови Python 3 і запусти PowerShell:

cd C:\openhab-smart-home
python -m pip install -r requirements.txt

Налаштуй параметри підключення до власного MQTT-брокера:

$env:MQTT_BROKER = "127.0.0.1"
$env:MQTT_PORT = "1884"
$env:MQTT_USERNAME = "sensor"
$env:MQTT_PASSWORD = "ВКАЖИ_СВІЙ_ПАРОЛЬ"

Заміни ВКАЖИ_СВІЙ_ПАРОЛЬ на пароль MQTT-користувача, налаштований у Mosquitto.

Запусти симулятор:

python scripts\sensor_simulator.py

Симулятор публікує дані кожні п'ять секунд:

MQTT-тема

Значення

home/kitchen/temperature

Температура в °C

home/kitchen/humidity

Вологість у %

home/kitchen/motion

Рух: ON або OFF

Запуск openHAB

Встанови Java 17.

Запусти openHAB.

Відкрий http://localhost:8080.

Налаштуй MQTT Broker Thing і підключення до Mosquitto.

Створи Items, правило сценаріїв та сторінку інтерфейсу.

Файли в config/ є прикладами конфігурації. Вони не встановлюються автоматично в робочий openHAB.

Безпека

Не зберігай паролі й токени в репозиторії.

Не додавай файли користувачів openHAB та приватні конфігурації.

Для реального використання налаштуй захищене підключення MQTT і обмеж доступ до брокера.


Статус

Навчальний проєкт. Датчики й освітлення можуть бути симульованими; фізичне обладнання не потрібне.