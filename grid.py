# Script for drawing a grid with the laser for calibration purposes
# Requires the python library from https://github.com/AnykeyNL/uArmProPython with the goto_laser-modification described in 'issue #1'

# Please, don't leave the arm unattended will operating the laser.

import uArmRobot

mode = 1

#Configure Serial port
#serialport = "com3"          # for windows 
serialport = "/dev/ttyACM0"  # for linux like system

# Connect to uArm 
myRobot = uArmRobot.robot(serialport)
myRobot.debug = True   # Enable / Disable debug output on screen, by default disabled
myRobot.connect()
myRobot.mode(mode)   # Set mode to Normal





gridSizeX = 150
gridSizeY = 200
gridOffsetX = 100

workingHeight = 150

# Horizontal lines 
for i in range(gridOffsetX/10, (gridOffsetX+gridSizeX)/10+1):
	print(i*10)
	myRobot.goto(i*10, -gridSizeY/2, workingHeight, 6000)
	myRobot.goto_laser(i*10, gridSizeY/2, workingHeight, 1500)
	myRobot.goto(i*10, gridSizeY/2, workingHeight, 6000) # Switch the laser off

# Vertical lines
for i in range(-gridSizeY/20, gridSizeY/20+1):
	print(i*10)
	myRobot.goto(gridOffsetX+gridSizeX, i*10, workingHeight, 6000)
	myRobot.goto_laser(gridOffsetX, i*10, workingHeight, 1500)
	myRobot.goto(gridOffsetX, i*10, workingHeight, 6000) # Switch the laser off

