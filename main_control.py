import time
import threading
from dual_g2_hpmd_rpi import motors, MAX_SPEED
from RPi import GPIO
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

encoder_pins = [17, 18, 14, 15]
button_pin = 27

GPIO.setmode(GPIO.BCM)
for pin in encoder_pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

class DriverFault(Exception):
    def __init__(self, driver_num):
        self.driver_num = driver_num

def raiseIfFault():
    if motors.motor1.getFault() or motors.motor2.getFault():
        motors.forceStop()
        raise DriverFault(1 if motors.motor1.getFault() else 2)

val_1 = MAX_SPEED // 4
val_2 = MAX_SPEED // 4
step_size = MAX_SPEED // 20

motors.setSpeeds(-val_1, val_2)

@app.route('/get')
def get_speed():
    return jsonify({'val_1': val_1, 'val_2': val_2})

@app.route('/set/<int:new_1>/<int:new_2>')
def set_speed(new_1, new_2):
    global val_1, val_2
    val_1, val_2 = new_1, new_2
    motors.setSpeeds(-val_1, val_2)
    return jsonify({'val_1': val_1, 'val_2': val_2})

@app.route('/stop')
def stop_motors():
    global val_1, val_2
    while val_1 > 0 or val_2 > 0:
        val_1 = max(0, val_1 - step_size)
        val_2 = max(0, val_2 - step_size)
        motors.setSpeeds(-val_1, val_2)
        time.sleep(0.3)
    return jsonify({'val_1': val_1, 'val_2': val_2})

def run_motors():
    global val_1, val_2
    clkLastState = [GPIO.input(encoder_pins[i]) for i in range(2)]
    button_pressed = False

    try:
        while True:
            clkState = [GPIO.input(encoder_pins[i]) for i in range(2)]
            dtState = [GPIO.input(encoder_pins[i+2]) for i in range(2)]

            for i in range(2):
                if clkState[i] != clkLastState[i]:
                    if dtState[i] != clkState[i]:
                        val = val_1 if i == 0 else val_2
                        val = min(MAX_SPEED, val + step_size)
                    else:
                        val = val_1 if i == 0 else val_2
                        val = max(0, val - step_size)

                    if i == 0:
                        val_1 = val
                        motors.motor1.setSpeed(-val_1)
                    else:
                        val_2 = val
                        motors.motor2.setSpeed(val_2)

                    raiseIfFault()
                    time.sleep(0.002)

            clkLastState = clkState
            button_pressed = not GPIO.input(button_pin)
            if button_pressed:
                stop_motors()

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