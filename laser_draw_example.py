import uArmLaserRobot

mode = 1

steps_per_seg = 10
x_offset = 170
height = 130
draw_speed = 3000
targetWidth = 70



#Configure Serial port
#serialport = "com3"          # for windows 
serialport = "/dev/ttyACM0"  # for linux like system

# Connect to uArm 
myRobot = uArmLaserRobot.laserRobot(serialport)
myRobot.debug = True   # Enable / Disable debug output on screen, by default disabled
myRobot.connect()
myRobot.mode(mode)   # Set mode to Normal

coords = myRobot.parseSVG('bird.svg', targetWidth, x_offset, steps_per_seg)

myRobot.set_path_start(coords, height)

myRobot.drawPath(coords, draw_speed, height, mode)

# The starting point
myRobot.loff()

