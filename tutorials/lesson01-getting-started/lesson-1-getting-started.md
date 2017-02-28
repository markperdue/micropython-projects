# Products used in this lesson
* NodeMCU ESP8266 <https://www.amazon.com/HiLetgo-Version-NodeMCU-Internet-Development/dp/B010O1G1ES>
* Micro USB cable <https://www.amazon.com/AmazonBasics-USB-Male-Micro-Cable/dp/B01EK87T9M>

# Getting started
1. Go to <http://micropython.org/download#esp8266> and download the latest stable .bin firmware for the ESP8266
2. Download and install the USB drivers from <https://www.silabs.com/products/mcu/Pages/USBtoUARTBridgeVCPDrivers.aspx> (direct link <https://www.silabs.com/documents/public/software/Mac_OSX_VCP_Driver.zip>)
3. Install esptool which provides an easy way of deploying files and firmware to the ESP8266
```
pip install esptool
```

# Deploying MicroPython
1. Power the ESP8266 with a USB cable connect to your computer
2. Verify that the ESP8266's USB port is detected by looking for a USB listing in /dev/. In my case the port is shown as /dev/tty.SLAB_USBtoUART
```
ls /dev/ | grep USB
```
3. It is best to erase any existing firmware before proceeding by running
```
esptool.py --port /dev/tty.SLAB_USBtoUART erase_flash
```
4. Deploy MicroPython using esptool
```
esptool.py --port /dev/tty.SLAB_USBtoUART --baud 460800 write_flash --flash_size=32m 0 esp8266-2017*.bin
```

# MicroPython REPL
1. To access a python prompt on the ESP8266 run the following
```
screen /dev/tty.SLAB_USBtoUART 115200
```
2. To verify the firmware integrity make sure the following returns True
```
import esp
esp.check_fw()
```

Note: To exit the REPL press Ctrl A + Ctrl \
