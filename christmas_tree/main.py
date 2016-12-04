import machine
from time import sleep

led = machine.Pin(14, machine.Pin.OUT)
adc = machine.ADC(0)

def flash_led(seconds):
    led.high()
    sleep(seconds)
    led.low()
    sleep(seconds)


while True:
    adc_value = adc.read()
    if adc_value is not None:
        if adc_value < 150:
            flash_led(0.125)
            flash_led(0.125)
            flash_led(0.125)
        elif adc_value < 250:
            flash_led(0.25)
            flash_led(0.25)
        elif adc_value < 350:
            flash_led(0.5)
        elif adc_value < 450:
            led.high()
        else:
            led.low()
    else:
        flash_led(1)

    sleep(.5)
