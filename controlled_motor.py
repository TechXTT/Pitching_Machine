import time
from dual_g2_hpmd_rpi import motors, MAX_SPEED

# Define a custom exception to raise if a fault is detected.
class DriverFault(Exception):
    def __init__(self, driver_num):
        self.driver_num = driver_num

def raiseIfFault():
    if motors.motor1.getFault():
        raise DriverFault(1)
    if motors.motor2.getFault():
        raise DriverFault(2)

try:
    motors.setSpeeds(0, 0)
    while True:
        inp = input("Enter speed for Motor 1: ")
        if inp == "q":
            break
        speed1 = int(inp)
        inp = input("Enter speed for Motor 2: ")
        if inp == "q":
            break
        speed2 = int(inp)
        motors.setSpeeds(speed1, speed2)
        raiseIfFault()
        time.sleep(0.002)

except DriverFault as e:
    print("Driver %s fault!" % e.driver_num)

finally:
    # Stop the motors, even if there is an exception
    # or the user presses Ctrl+C to kill the process.
    motors.forceStop()
