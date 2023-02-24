from RPi import GPIO
from time import sleep

in1 = 24
in2 = 23
en = 25
temp1 = 1

encoder_clk = 17
encoder_data = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(en, GPIO.OUT)
GPIO.setup(encoder_clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(encoder_data, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.output(in1, GPIO.LOW)
GPIO.output(in2, GPIO.LOW)

p = GPIO.PWM(en, 1000)
p.start(25)

val = 25

step_size = 5

clkLastState = GPIO.input(encoder_clk)

try:
    while True:
        # use the rotary encoder to control the speed
        clkState = GPIO.input(encoder_clk)
        dtState = GPIO.input(encoder_data)
        if clkState != clkLastState:
            if dtState != clkState:
                val = val + step_size
            else:
                val = val - step_size
            print(val)
            if val > 100:
                val = 100
            if val > 0:
                GPIO.output(in1, GPIO.HIGH)
                GPIO.output(in2, GPIO.LOW)
                print("forward")
                p.ChangeDutyCycle(val)
            elif val < 0:
                GPIO.output(in1, GPIO.LOW)
                GPIO.output(in2, GPIO.HIGH)
                print("backward")
                p.ChangeDutyCycle(-val)
            else:
                GPIO.output(in1, GPIO.LOW)
                GPIO.output(in2, GPIO.LOW)
                print("stop")
        clkLastState = clkState
        sleep(0.01)
finally:
    GPIO.cleanup()
