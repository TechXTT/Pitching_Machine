from RPi import GPIO
from time import sleep

encoder_clk = 17
encoder_data = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(encoder_clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(encoder_data, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

val = 0

step_size = 5

clkLastState = GPIO.input(encoder_clk)

try:
    while True:
        clkState = GPIO.input(encoder_clk)
        dtState = GPIO.input(encoder_data)
        if clkState != clkLastState:
            if dtState != clkState:
                val = val + step_size
            else:
                val = val - step_size
            print(val)
        clkLastState = clkState
        sleep(0.01)
finally:
    GPIO.cleanup()
    