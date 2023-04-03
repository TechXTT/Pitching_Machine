import time
from dual_g2_hpmd_rpi import motors, MAX_SPEED
from RPi import GPIO

encoder_clk_1 = 17
encoder_data_1 = 18
encoder_clk_2 = 27
encoder_data_2 = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(encoder_clk_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(encoder_data_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(encoder_clk_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(encoder_data_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Define a custom exception to raise if a fault is detected.
class DriverFault(Exception):
    def __init__(self, driver_num):
        self.driver_num = driver_num

def raiseIfFault():
    if motors.motor1.getFault():
        raise DriverFault(1)
    if motors.motor2.getFault():
        raise DriverFault(2)

val = MAX_SPEED / 4 # start at 25% speed
 
step_size = MAX_SPEED / 120 # 4/480 speed per step

clkLastState_1 = GPIO.input(encoder_clk_1)
clkLastState_2 = GPIO.input(encoder_clk_2)

try:
    while True:
        clkState_1 = GPIO.input(encoder_clk_1)
        dtState_1 = GPIO.input(encoder_data_1)
        clkState_2 = GPIO.input(encoder_clk_2)
        dtState_2 = GPIO.input(encoder_data_2)
        if clkState_1 != clkLastState_1:
            if dtState_1 != clkState_1:
                val = val + step_size
            else:
                val = val - step_size
            print('Motor 1: ' + str(val))
            if val > MAX_SPEED:
                val = MAX_SPEED
            motors.setSpeeds(val, val)
            raiseIfFault()
            time.sleep(0.002)
        clkLastState_1 = clkState_1
        if clkState_2 != clkLastState_2:
            if dtState_2 != clkState_2:
                val = val + step_size
            else:
                val = val - step_size
            print('Motor 2: ' + str(val))
            if val > MAX_SPEED:
                val = MAX_SPEED
            motors.setSpeeds(val, val)
            raiseIfFault()
            time.sleep(0.002)
        clkLastState_2 = clkState_2
        time.sleep(0.01)


except DriverFault as e:
    print("Driver %s fault!" % e.driver_num)

finally:
    motors.forceStop()
    GPIO.cleanup()