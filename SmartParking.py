"""
Assignment Title: Gestion de parking intelligent
Purpose         : Implementation of Smart Parking
Language        : Python
Author          : Hemant Ramphul
Github          : https://github.com/hemantramphul/Smart-Parking/
Date            : 05 January 2023

Université des Mascareignes (UdM)
Faculty of Information and Communication Technology
Master Artificial Intelligence and Robotics
Official Website: https://udm.ac.mu
"""

import RPi.GPIO as GPIO  # Importing the library of RPi.GPIO
import time  # Importing the library of time
import serial  # Importing the library of time
import string  # Importing the library string
import random  # Importing the library random
import os  # Importing the library os
from datetime import datetime  # Importing the library datetime

# Format to store date
fmt = '%Y-%m-%d %H:%M:%S'

# Filename
fileLogReserve = "log-reserve.txt"  # Log all reserved parking info
fileLogCancel = "log-cancel.txt"  # Log all cancellation parking info

# [True] -> Reservation mode
# [False] ->  Unlock mode
modeUnlockOrReserve = True

# Parking
parkingOneAvailable = True
parkingTwoAvailable = True

led = 17  # Declaring GPIO 17 of Raspberry Pi
sensor = 27  # Declaring GPIO 27 of Raspberry Pi

GPIO.setmode(GPIO.BCM)  # Declaring the BCM mode of pins
GPIO.setwarnings(False)  # Disabled warning
GPIO.setup(sensor, GPIO.IN)  # Set the behaviour of sensor as input
GPIO.setup(led, GPIO.OUT)  # Set the behaviour of led as output


def secretCode(length=4):
    """
    Function to generate a secret code
    :param length: 4 is the default number
    :return: String [secret code]
    """
    # Choose from all digits 0123456798
    letters = string.digits
    # Generate secret code
    code = ''.join(random.choice(letters) for i in range(length))

    return code  # Generated secret code


def sensorCheck():
    """
    Function to check if a car is near sensor
    :return: boolean [True or False]
    """
    try:
        while GPIO.input(sensor):  # Checking input on sensor
            GPIO.output(led, False)  # Led turned on
            while GPIO.input(sensor):  # Checking input on sensor again
                time.sleep(0.2)  # Time delay of 0.2 seconds
        GPIO.output(led, True)  # Led turned off if there is no input on sensor
    except KeyboardInterrupt:  # If any key is pressed on keyboard terminate the program
        GPIO.cleanup()  # Cleanup the GPIO pins for any other program use

    return GPIO.input(sensor)


def splitLog(line):
    """
    Function to split line contains ";"
    :param line:
    :return: array
    """
    return line.split(';')


def CheckParkingExpiredTime(reserved_time):
    """
    Function to check expired date with 15 seconds
    :param reserved_time:
    :return: boolean [True or False]
    """
    # Check expiration time
    t = datetime.now()
    expired = datetime.strftime(t, fmt) - datetime.strptime(reserved_time, fmt)
    # Returns the difference of the time
    minutes = divmod(expired.seconds, 60)

    # Check if time have pass 15 seconds
    return True if minutes[1] > 15 else False


def readResponse():
    """
    Function to read Arduino response
    :return:
    """
    while arduino.inWaiting() == 0: pass  # Wait for Arduino to answer if any
    if arduino.inWaiting() > 0:
        answer = arduino.readline()  # Read answer
        print("{}".format(answer))  # Display answer


def writeToFile(code, parking):
    """
    Function to write to a log file [Reserve]
    :param code: secret code
    :param parking: Parking number
    :return:
    """
    fileToWrite = open(fileLogReserve, "a")  # Append mode
    # Save record like "code,parking_number,reserved,datetime"
    fileToWrite.write(code + ";" + parking + ";Reserved;" + str(datetime.strftime(datetime.now(), fmt)) + "\n")
    fileToWrite.close()  # Close file connection


def writeToFileCancel(line):
    """
    Function to write to a log file [Cancellation]
    :param line: log
    :return:
    """
    fileToWrite = open(fileLogCancel, "a")  # Append mode
    slotInfo = splitLog(line)  # Split line to takes some info
    fileToWrite.write(
        slotInfo[0] + ";" + slotInfo[1] + ";Canceled;" + str(datetime.strftime(datetime.now(), fmt)) + "\n")
    fileToWrite.close()  # Close file connection


def deleteLine(code):
    """
    Function to delete a line in log file
    :param code: secret code
    :return: boolean, String
    """
    log = ""
    deleted = False
    with open(fileLogReserve, "r") as input:  # Read from file
        with open("temp.txt", "w") as output:  # Use a temp file
            # Iterate all lines from file
            for line in input:
                if line.strip("\n").startswith(code):
                    log = line
                    writeToFileCancel(line)
                    deleted = True
                # If line starts with substring 'code' then don't write it in temp file
                if not line.strip("\n").startswith(code):
                    output.write(line)

    # Replace file with original name
    os.replace('temp.txt', fileLogReserve)

    return deleted, log


def searchLog(code):
    """
    Function to search line in log file
    :param code: secret code
    :return: String
    """
    log = ""
    with open(fileLogReserve, "r") as input:
        for line in input:
            # If line contain Secret Code
            if line.strip("\n").startswith(code):
                log = line

    return log


# Main application start
if __name__ == '__main__':
    print('Smart Parking System. \nStatus [Running]. Press CTRL-C to exit.\n')  # App info
    GPIO.output(led, True)  # Led turned on

    arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # Connect to Arduino via specific port
    arduino.reset_input_buffer()

    time.sleep(0.1)
    if arduino.isOpen() and not sensorCheck():
        print("{} connected!".format(arduino.port))  # Check Arduino if is well connected

        try:
            # Show message for mode option
            print(
                '[*] Type "R" to enter reservation mode. \n[*] Type "U" to enter unlock mode. \n[*] Type "C" to enter '
                'cancelation mode.\n')

            while True:
                # User input according to option available
                userInput = input('Enter MODE "R" or "U" or "C": ')

                # Parking canceled
                if userInput.upper() == 'C':
                    # Enter secret code
                    userCode = input('Enter Secret Code: ')
                    deleted, log = deleteLine(userCode)  # Call function deleteLine to cancel reservation
                    slotInfo = splitLog(log)  # Split line to take some info
                    if deleted:
                        print(slotInfo[1], 'canceled.\n')
                        if slotInfo[1] == 'Parking 1':  # Check which car Parking to cancel according to the secret code
                            arduino.write(b'1P1')  # Send Arduino information to perform
                            parkingOneAvailable = not parkingOneAvailable
                        else:
                            arduino.write(b'1P2')  # Send Arduino information to perform
                            parkingTwoAvailable = not parkingTwoAvailable
                    else:  # If secret code not found
                        print('Invalid secret code!\n')

                # Parking Reservation
                elif userInput.upper() == 'R':
                    # Enter Parking number
                    print('[*] Type "1" for Parking 1. \n[*] Type "2" for Parking 2. \n')
                    userParkingInput = input('Enter PARKING "1" or "2": ')
                    code = secretCode()  # Generate secret code
                    available = False
                    saveMsg = "Parking " + userParkingInput
                    msg = ""

                    if userParkingInput == "1" and parkingOneAvailable:
                        parkingOneAvailable = not parkingOneAvailable
                        available = True
                        arduino.write(b'2P1')  # Send Arduino information to perform
                        readResponse()  # Read Arduino response
                        writeToFile(code, saveMsg)  # Write to log file
                    elif userParkingInput == "2" and parkingTwoAvailable:
                        parkingTwoAvailable = not parkingTwoAvailable
                        available = True
                        arduino.write(b'2P2')  # Send Arduino information to perform
                        readResponse()  # Read Arduino response
                        writeToFile(code, saveMsg)  # Write to log file
                    elif not parkingOneAvailable and not parkingTwoAvailable:
                        # Check if parking available or full
                        msg = "Parking full!"
                    else:
                        # Check selected parking
                        msg = "Selected parking is not available."

                    print(msg)
                    print("Secret Code: " + code if available else "")
                    print('----------------------------------\n')

                    modeUnlockOrReserve = True
                # Parking Unlock
                elif userInput.upper() == 'U':
                    # Enter secret code
                    userCode = input('Enter Secret Code: ')
                    log = searchLog(userCode)  # Search information about the Parking reserved with the secret code

                    if log != "":
                        available = False
                        # Get information in array
                        slotInfo = splitLog(log)

                        # Check expired date
                        if CheckParkingExpiredTime(slotInfo[3].strip()):
                            print('Secret Code expired!\n')
                        else:
                            if slotInfo[1] == 'Parking 1':
                                arduino.write(b'3P1')  # Send Arduino information to perform
                            else:
                                arduino.write(b'3P2')  # Send Arduino information to perform

                        readResponse()
                        deleted, log = deleteLine(userCode)  # Delete log in log file

                    modeUnlockOrReserve = False
                else:
                    print('Invalid option!\n')
                    print('----------------------------------\n')

        except KeyboardInterrupt:
            print("KeyboardInterrupt has been caught.")
