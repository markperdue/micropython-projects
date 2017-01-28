import machine
import time

led = machine.Pin(14, machine.Pin.OUT)
button = machine.Pin(12, machine.Pin.IN)

prev_input = 0

while True:
    current_value = button.value()
    if ((not prev_input) and current_value):
        led.value(not led.value())

    prev_input = current_value
    time.sleep(0.05)