# Extensions to the uArm Swift Pro library by: Richard Garsthagen
# uArm Swift Pro - Python Library
# Created by: Richard Garsthagen - the.anykey@gmail.com
# V0.2 - June 2017 - Still under development
#
# Extension authored by Ossi Lehtinen.
# The laser cuts holes to stuff. Use at your own risk and don't leave unattended.



import uArmRobot
import protocol_swiftpro as protocol
from svgpathtools import svg2paths, wsvg
import numpy as np
import time
from PIL import Image  

class laserRobot(uArmRobot.robot):
	
    delay_after_move = 0.0
    
    def goto_laser(self,x,y,z,speed):
        self.moving = True
        x = str(round(x, 2))
        y = str(round(y, 2))
        z = str(round(z, 2))
        s = str(round(speed, 2))
        cmd = protocol.SET_POSITION_LASER.format(x,y,z,s)
        self.sendcmd(cmd, True)

    def loff(self):
        self.goto(200,0,150,6000)
            
    def parseSVG(self, filename, targetWidth, x_offset, steps_per_seg):

        # Parse the path
        paths, attributes = svg2paths(filename)


        # Find the bounding box
        xmin = 100000
        xmax = -10000
        ymin = 10000
        ymax = -10000

        for i in range(len(paths)):
            path = paths[i]
            attribute = attributes[i]
            # A crude check for wether a path should be drawn. Does it have a style defined? This caused trouble elsewhere...
            for seg in path:
                for p in range(steps_per_seg+1):
                    cp = seg.point(float(p)/float(steps_per_seg))
                    cx = np.real(cp)
                    cy = np.imag(cp)
                    if(cx < xmin): xmin = cx
                    if(cy < ymin): ymin = cy
                    if(cx > xmax): xmax = cx
                    if(cy > ymax): ymax = cy


        # The scaling factor to reach the targetWidth
        scale = targetWidth/(xmax-xmin)
                
        # Transform the paths to lists of coordinates
        coords = []

        for i in range(len(paths)):
            path = paths[i]
            attribute = attributes[i]
            # A crude check for wether a path should be drawn. Does it have a style defined?
            for seg in path:
                segcoords = []
                for p in range(steps_per_seg+1):
                    cp = seg.point(float(p)/float(steps_per_seg))
                    segcoords.append([scale*(np.real(cp)-xmin)+x_offset, scale*(np.imag(cp)-ymin) - scale*((ymax-ymin)/2.0)])
                coords.append(segcoords)

        return coords



    def set_path_start(self, coords, height, mode):
        
        move_lift = 0
        if(mode == 0):
            move_lift = 5
        
        self.goto(coords[0][0][0], coords[0][0][1], height+move_lift*2, 6000)
        
        if(mode == 1):
            for i in range(0, 5):
                self.goto_laser(coords[0][0][0], coords[0][0][1], height+move_lift*2, 6000)
                #time.sleep(0.0001)
                self.goto(coords[0][0][0], coords[0][0][1], height+move_lift*2, 6000)
                time.sleep(1.0)


    def drawPath(self, coords, draw_speed, height, mode):

        # Lift the pen if using one
        move_lift = 0
        if(mode == 0):
            move_lift = 3

        
        # The starting point
        self.goto(coords[0][0][0], coords[0][0][1], height+move_lift*2, 6000)

        lastCoord = coords[0][0]

        epsilon = 0.1
        #if(abs(seg[0][0] - lastCoord[0]) > epsilon and abs(seg[0][1] - lastCoord[1]) > epsilon):

        for seg in coords:    
            if(abs(seg[0][0] - lastCoord[0]) > epsilon and abs(seg[0][1] - lastCoord[1]) > epsilon):
                self.goto(lastCoord[0], lastCoord[1], height+move_lift, 6000)
                self.goto(seg[0][0], seg[0][1], height+move_lift, 6000)
                 # Not sure if this helps with anything, but the idea is to give the arm a moment after a long transition
                time.sleep(0.15)
            for p in seg:
                self.goto_laser(p[0], p[1], height, draw_speed)
            lastCoord = p


        # Back to the starting point (and turn the laser off)
        self.goto(lastCoord[0], lastCoord[1], height+move_lift*2, 6000)
        self.goto(coords[0][0][0], coords[0][0][1], height+move_lift*2, 6000)
	
    def drawBitmap(self, imagepath, printSizeX, lineSpacing, xOffset, height, draw_speed, mode):
		
        # Lift the pen if using one
        move_lift = 0
        if(mode == 0):
            move_lift = 3

                
        im = Image.open(imagepath)   

        smallImSizeX = printSizeX*2 # Determines the resolution of the dithering

        scale = float(smallImSizeX)/float(im.size[0])

        im2 = im.resize( (int(scale*im.size[0]), int(scale*im.size[1])) )
        im = im2.convert("1")

        imageSizeX = im.size[0]
        imageSizeY = im.size[1]

        scale = float(printSizeX)/float(imageSizeX)

        printSizeY = imageSizeY*scale
        yOffset = -printSizeY/2

        # Y-direction
        for j in range(int(yOffset/lineSpacing), -int(yOffset/lineSpacing)+1):
            
            cY = j*lineSpacing
            print(cY)
            
            cp = 0
            nextp = cp+1
            cpVal = im.getpixel((cp, int((cY-yOffset)/scale)))
            self.goto(xOffset, cY, height+move_lift, 6000)
            
            while(cp < imageSizeX-1):
                
                while(im.getpixel((nextp, int((cY-yOffset)/scale)))==cpVal and nextp < imageSizeX-1):
                    nextp = nextp + 1
                
                if(cpVal == 0):
                    self.goto_laser(prevX, prevY, height, draw_speed)
                    self.goto_laser(xOffset+nextp*scale, cY, height, draw_speed)
                    self.goto(xOffset+nextp*scale, cY, height+move_lift, draw_speed)
                else:
                    self.goto(xOffset+nextp*scale, cY, height+move_lift, 6000)
                
                prevX = xOffset+nextp*scale
                prevY = cY
                
                self.goto(prevX, prevY, height+move_lift, 6000)
                cp = nextp
                cpVal = im.getpixel((cp, int((cY-yOffset)/scale)))


        # X-direction
        for j in range(int(xOffset/lineSpacing), int((xOffset+printSizeX)/lineSpacing)):
            
            cX = j*lineSpacing
            print(cX)
            
            cp = 0
            nextp = cp+1
            cpVal = im.getpixel((int((cX-xOffset)/scale), cp))
            self.goto(cX, yOffset, height+move_lift, 6000)
            
            while(cp < imageSizeY-1):
                
                while(im.getpixel((int((cX-xOffset)/scale), nextp))==cpVal and nextp < imageSizeY-1):
                    nextp = nextp + 1
                
                if(cpVal == 0):
                    self.goto_laser(prevX, prevY, height, draw_speed)
                    self.goto_laser(cX, yOffset+nextp*scale, height, draw_speed)
                    self.goto(cX, yOffset+nextp*scale, height+move_lift, draw_speed)
                else:
                    self.goto(cX, yOffset+nextp*scale, height+move_lift, 6000)
                
                prevX = cX
                prevY = yOffset+nextp*scale
                
                self.goto(prevX, prevY, height+move_lift, 6000)
                cp = nextp
                cpVal = im.getpixel((int((cX-xOffset)/scale), cp))





        self.loff()






