import time
import threading
from dual_g2_hpmd_rpi import motors, MAX_SPEED
from RPi import GPIO
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

encoder_clk_1 = 17
encoder_data_1 = 18
button = 27
encoder_clk_2 = 14
encoder_data_2 = 15

GPIO.setmode(GPIO.BCM)
GPIO.setup(encoder_clk_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(encoder_data_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
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

val_1 = MAX_SPEED / 4 # start at 25% speed
val_2 = MAX_SPEED / 4 # start at 25% speed

step_size = MAX_SPEED / 20 # 24 speed per step

clkLastState_1 = GPIO.input(encoder_clk_1)
clkLastState_2 = GPIO.input(encoder_clk_2)
button_pressed = False

motors.setSpeeds(-val_1, val_2)

@app.route('/get')
def index():
    # return json data
    return {'val_1': val_1, 'val_2': val_2}

@app.route('/set/<int:new_1>/<int:new_2>')
def set(new_1, new_2):
    global val_1, val_2
    val_1 = new_1
    val_2 = new_2
    motors.setSpeeds(-val_1, val_2)
    return {'val_1': val_1, 'val_2': val_2}

@app.route('/stop')
def stop():
    global val_1, val_2
    while val_1 > 0 or val_2 > 0:
        val_1 = val_1 - step_size
        val_2 = val_2 - step_size
        if val_1 < 0:
            val_1 = 0
        if val_2 < 0:
            val_2 = 0

        motors.setSpeeds(-val_1, val_2)
        time.sleep(0.3)

    return {'val_1': val_1, 'val_2': val_2}

def run_motors():
    global val_1, val_2, clkLastState_1, clkLastState_2, button_pressed

    try:
        while True:
            clkState_1 = GPIO.input(encoder_clk_1)
            dtState_1 = GPIO.input(encoder_data_1)
            
            clkState_2 = GPIO.input(encoder_clk_2)
            dtState_2 = GPIO.input(encoder_data_2)
            
            if clkState_1 != clkLastState_1:
                if dtState_1 != clkState_1:
                    val_1 = val_1 + step_size
                else:
                    val_1 = val_1 - step_size

                if val_1 >= MAX_SPEED:
                    val_1 = MAX_SPEED
                if val_1 <= 0:
                    val_1 = 0

                motors.motor1.setSpeed(-val_1)
                raiseIfFault()
                time.sleep(0.002)
                
            if clkState_2 != clkLastState_2:
                if dtState_2 != clkState_2:
                    val_2 = val_2 + step_size
                else:
                    val_2 = val_2 - step_size

                if val_2 >= MAX_SPEED:
                    val_2 = MAX_SPEED
                if val_2 <= 0:
                    val_2 = 0

                motors.motor2.setSpeed(val_2)
                raiseIfFault()
                time.sleep(0.002)


            clkLastState_1 = clkState_1
            clkLastState_2 = clkState_2
            button_pressed = not GPIO.input(button)
            if button_pressed :
                # Stop the motors slowly.
                while val_1 > 0 or val_2 > 0:
                    val_1 = val_1 - step_size
                    val_2 = val_2 - step_size

                    if val_1 < 0:
                        val_1 = 0
                    if val_2 < 0:
                        val_2 = 0
                    
                    motors.setSpeeds(-val_1, val_2)
                    time.sleep(0.3)

            time.sleep(0.01)

    except DriverFault as e:
        print("Driver %s fault!" % e.driver_num)

    finally:
        motors.forceStop()
        GPIO.cleanup()

thread = threading.Thread(target=run_motors)
thread.daemon = True
thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
