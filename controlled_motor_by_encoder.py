import time
from dual_g2_hpmd_rpi import motors, MAX_SPEED
from RPi import GPIO

encoder_clk_1 = 17
encoder_data_1 = 18
encoder_clk_2 = 27
encoder_data_2 = 22
button = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(encoder_clk_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(encoder_data_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(encoder_clk_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(encoder_data_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Define a custom exception to raise if a fault is detected.
class DriverFault(Exception):
    def __init__(self, driver_num):
        self.driver_num = driver_num

def raiseIfFault():
    if motors.motor1.getFault():
        raise DriverFault(1)
    if motors.motor2.getFault():
        raise DriverFault(2)

val_1 = MAX_SPEED / 2 # start at 50% speed
val_2 = MAX_SPEED / 2 # start at 50% speed
 
step_size = MAX_SPEED / 30 # 16 speed per step

clkLastState_1 = GPIO.input(encoder_clk_1)
clkLastState_2 = GPIO.input(encoder_clk_2)

button_pressed = False

try:
    while not button_pressed:
        clkState_1 = GPIO.input(encoder_clk_1)
        dtState_1 = GPIO.input(encoder_data_1)
        clkState_2 = GPIO.input(encoder_clk_2)
        dtState_2 = GPIO.input(encoder_data_2)
        if clkState_1 != clkLastState_1:
            if dtState_1 != clkState_1:
                val_1 = val_1 + step_size
            else:
                val_1 = val_1 - step_size
            print('Motor 1: ' + str(val_1))
            if val_1 >= MAX_SPEED:
                val_1 = MAX_SPEED
            if val_1 <= 0:
                val_1 = 0
            motors.motor1.setSpeed(-val_1)
            raiseIfFault()
            time.sleep(0.002)
        clkLastState_1 = clkState_1
        if clkState_2 != clkLastState_2:
            if dtState_2 != clkState_2:
                val_2 = val_2 + step_size
            else:
                val_2 = val_2 - step_size
            print('Motor 2: ' + str(val_2))
            if val_2 >= MAX_SPEED:
                val_2 = MAX_SPEED
            if val_1 <= 0:
                val_1 = 0
            motors.motor2.setSpeed(val_2)
            raiseIfFault()
            time.sleep(0.002)
        clkLastState_2 = clkState_2

        if GPIO.input(button) == GPIO.LOW:
            button_pressed = True
            print('Button pressed')

        time.sleep(0.01)
    else:
        # Stop the motors slowly.
        while val_1 > 0 or val_2 > 0:
            val_1 = val_1 - step_size
            val_2 = val_2 - step_size
            if val_1 < 0:
                val_1 = 0
            if val_2 < 0:
                val_2 = 0
            motors.setSpeeds(val_1, val_2)
            raiseIfFault()
            time.sleep(0.01)


except DriverFault as e:
    print("Driver %s fault!" % e.driver_num)

finally:
    motors.forceStop()
    GPIO.cleanup()