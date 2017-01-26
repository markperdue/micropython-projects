light_switch_toggle
===================

Toggles a power outlet that is provided by a DLI IoT Relay. An ESP8266 is connected to a push button switch which has leads going to the DLI IoT Relay


Parts List
----------

- ESP8266 (NodeMCUv2)
- DLI IoT Relay (https://www.amazon.com/Iot-Relay-Enclosed-High-power-Raspberry/dp/B00WV7GMA2)
- Breadboard
- Wire leads


Installation
------------

1. Flash micropython firmware on to the ESP8266.
2. Copy main.py to the root directory of the micropython firmware running on the ESP8266. Check out the `ampy <https://github.com/adafruit/ampy>`_ project for an easy cli tool to copy files