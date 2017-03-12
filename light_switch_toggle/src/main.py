import machine
from time import sleep

led = machine.Pin(14, machine.Pin.OUT)
button = machine.Pin(12, machine.Pin.IN)


def main():
    prev_input = 1  # Set start to 1 for ESP8266

    while True:
        current_value = button.value()
        if (not prev_input) and current_value:
            led.value(not led.value())

        prev_input = current_value
        sleep(0.25)


if __name__ == '__main__':
    main()