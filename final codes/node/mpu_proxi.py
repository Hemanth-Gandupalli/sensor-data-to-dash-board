# -*- coding: utf-8 -*-
import smbus
import time,json
from datetime import datetime
import RPi.GPIO as GPIO
import threading

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
stp = 5
Tht = 6
IGN = 19
GPIO.setup(Tht, GPIO.OUT)
GPIO.setup(IGN, GPIO.OUT)
GPIO.setup(stp, GPIO.OUT)
# I2C address of the MPU9250


GPIO.setmode(GPIO.BCM)

# Define GPIO pins for interrupts
interrupt_pins = [17, 13, 23, 27, 18]

# Global variables for each sensor
pulses = [0] * 5
last_times = [0] * 5
pulses_per_revolution = 1

#------------------------------------------------------------------------------------
def mpu():
        MPU9250_ADDRESS = 0x68

        # Register addresses for the accelerometer data
        ACCEL_XOUT_H = 0x3B

        bus = smbus.SMBus(1)  # Use bus 1 for Raspberry Pi 3, 4, or 400
        bus.write_byte_data(MPU9250_ADDRESS, 0x6B, 0)

        # Initial calibration: Read and discard initial values
        calibration_values = bus.read_i2c_block_data(MPU9250_ADDRESS, ACCEL_XOUT_H, 6)
        print("Calibration Values:", calibration_values)

        while True:
            # Read accelerometer data
            accel_data = bus.read_i2c_block_data(MPU9250_ADDRESS, ACCEL_XOUT_H, 6)

            # Combine high and low bytes for each axis
            AcX = accel_data[0] << 8 | accel_data[1]
            AcY = accel_data[2] << 8 | accel_data[3]
            AcZ = accel_data[4] << 8 | accel_data[5]

            # Subtract the calibration values
            AcX -= calibration_values[0] << 8 | calibration_values[1]
            AcY -= calibration_values[2] << 8 | calibration_values[3]
            AcZ -= calibration_values[4] << 8 | calibration_values[5]

            # Scale the accelerometer data based on the full-scale range (±2g)
            scale_factor = 2.0 / 32768.0  # 32768 is the maximum value for a 16-bit signed integer
            AcX = AcX * scale_factor
            AcY = AcY * scale_factor
            AcZ = AcZ * scale_factor

            # Print the raw accelerometer data and scaled values
            print(f"Raw Acceleration - X: {accel_data[0]}, Y: {accel_data[2]}, Z: {accel_data[4]}")
            print(f"Scaled Acceleration - X: {AcX:.2f} g, Y: {AcY:.2f} g, Z: {AcZ:.2f} g")
            with open("mdata.json",'r') as f:
                data = json.load(f)
            data["X"] = abs(round(AcX,2))
            data["Y"] = abs(round(AcY,2))
            data["Z"] = abs(round(AcZ,2))
            with open("mdata.json",'w') as f:
                json.dump(data,f)
            time.sleep(15)  # Delay for 1 second
#----------------------------------------------------------------------------------
def proxi():
    def count_pulse(channel):
        global pulses, last_times

        sensor_index = interrupt_pins.index(channel)
        current_time = time.time() * 1000  # Convert seconds to milliseconds

        if current_time - last_times[sensor_index] >= 1000:
            rpm = (pulses[sensor_index] * 60.0) / ((current_time - last_times[sensor_index]) / 1000.0) / pulses_per_revolution

            print(f"Sensor {sensor_index + 1} RPM: {round(rpm,2)}")
            sense_num = sensor_index + 1
            with open ('data.json','r') as file:
                data = json.load(file)
            data[sense_num] = round(rpm,2)
            with open('data.json','w') as file:
                json.dump(data,file)
            pulses[sensor_index] = 0
            last_times[sensor_index] = current_time

        pulses[sensor_index] += 1
        #time.sleep(0.1)

    # Set up GPIO pins for input with pull-up resistors and add event detection
    for pin in interrupt_pins:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=count_pulse)

    try:
        print("Waiting for interrupts...")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        # Handle keyboard interrupt (Ctrl+C)
        GPIO.cleanup()
        print("\nProgram terminated by user.")
#-----------------------------------------------------------------------------------------------   
#    GPIO.output(stp, GPIO.LOW)
def timer():
    while True:
        GPIO.output(IGN, GPIO.HIGH)
        time.sleep(3)
        GPIO.output(Tht, GPIO.HIGH)
        print("max")
        time.sleep(2)
        GPIO.output(IGN, GPIO.LOW)
        GPIO.output(Tht, GPIO.LOW)
        print("STOP")
        time.sleep(10)
    #    GPIO.output(stp, GPIO.HIGH)
        GPIO.output(IGN, GPIO.LOW)
        GPIO.output(Tht, GPIO.LOW)
        print("Device OFF")
        
threading.Thread(target = mpu).start()
threading.Thread(target = proxi).start()
threading.Thread(target = timer).start()