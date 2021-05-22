# Ching Pang (cp546) Michelle DeSouza (md722)
import RPi.GPIO as GPIO
import time
import os
import sys, pygame
import cv2
import numpy as np
import subprocess

# showing on piTFT
os.putenv('SDL_VIDEORIVER','fbcon')
os.putenv('SDL_FBDEV','/dev/fb0')
os.putenv('SDL_MOUSEDRV','TSLIB')
os.putenv('SDL_MOUSEDEV','/dev/input/touchscreen')

GPIO.setmode(GPIO.BCM)
# bail out button
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# correspond to on screen button for level 2
#GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
def GPIO17_callback(channel):
	global running
	print("quit with bail out button")
	running = 0
	GPIO.cleanup()
# on screen buttons for level 2 detection
#GPIO.add_event_detect(27,GPIO.FALLING, callback=GPIO27_callback)
#GPIO.add_event_detect(23,GPIO.FALLING, callback=GPIO23_callback)
#GPIO.add_event_detect(22,GPIO.FALLING, callback=GPIO22_callback)
# bail out button detection
GPIO.add_event_detect(17,GPIO.FALLING,callback=GPIO17_callback,bouncetime=400)

# pygame setup choosing number
pygame.init()

size = width,height = 320,240
screen = pygame.display.set_mode(size)
small_font = pygame.font.Font(None, 25)
big_font = pygame.font.Font(None, 35)
white = 255,255,255
black = 0,0,0
red = 255,0,0
green = 0, 255, 0
pygame.mouse.set_visible(False)
global running
running = 1
num = "01"
#global num
#global numhist
numhist = ["01"]
# buttons and positions on screen
buttons = {"1": (25,160),"2": (75,160),"3": (125,160),"4": (175,160),"5": (225,160),
	"6":(25,200),"7":(75,200),"8":(125,200),"9":(175,200),"0":(225,200),
	"confirm":(275,160), "reset":(275,200)}
static = {"Number of slices(max 16)": (120,30)}
numpos = (160,100)
warningpos = (160,130)
def updatenum(newnum,number,numhistory):
	global numhist
	global num
	lastchar = number[-1]
	number= lastchar +str(newnum)
#	numhist = [num]
	numhistory.pop(0)
	numhistory.append(number)
	num = number
	numhist = numhistory
	print newnum,number, numhistory
while running:
	time.sleep(0.001)
	screen.fill(black)
	#text for number of slices
	for text,position in static.items():
		display_text = small_font.render(text,True,white)
		rect = display_text.get_rect(center = position)
		screen.blit(display_text,rect)
	# text for options
	for text,position in buttons.items():
		display_sel = small_font.render(text,True,white)
		selrect = display_sel.get_rect(center = position)
		screen.blit(display_sel,selrect)
	# getting the number
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		elif event.type == pygame.MOUSEBUTTONUP:
			pos = pygame.mouse.get_pos()
			xpos, ypos = pos
			if ypos>140 and ypos<180: #torow
				if xpos > 5 and xpos <50:
					updatenum(1,num,numhist)
				elif xpos > 50 and xpos < 100:
					updatenum(2,num,numhist)
				elif xpos >100 and xpos <150:
					updatenum(3,num,numhist)
				elif xpos > 150 and xpos <200:
					updatenum(4,num,numhist)
				elif xpos > 200 and xpos <250:
					updatenum(5,num,numhist)
				elif xpos > 250 and xpos <300:
					# something to confirm and move on to camera
					print('confirm')
					running = 0
			elif ypos > 180 and ypos <220:
				if xpos > 5 and xpos <50:
                                        updatenum(6,num,numhist)
                                elif xpos > 50 and xpos < 100:
                                        updatenum(7,num,numhist)
                                elif xpos >100 and xpos <150:
                                        updatenum(8,num,numhist)
                                elif xpos > 150 and xpos <200:
                                        updatenum(9,num,numhist)
                                elif xpos > 200 and xpos <250:
                                        updatenum(0,num,numhist)
                                elif xpos > 250 and xpos <300:
                                        num = "00" # reset number
					numhist = [num]
					print('reset')
# update number
        display_num = big_font.render(numhist[0],True,white)
        num_rect = display_num.get_rect(center = numpos)
        screen.blit(display_num,num_rect)


	if int(num)>16:
		num = '01'
		numhist = [num]
		warningtext = 'input number <=16'
	elif int(num)==0:
		num = '01'
		numhist = [num]
		warningtext = 'input number > 1'
	else:
		warningtext = 'max slices:16'
	displaywarning = small_font.render(warningtext,True,white)
	warningrect = displaywarning.get_rect(center = warningpos)
	screen.blit(displaywarning,warningrect)
	pygame.display.flip()
print('clean up')
GPIO.cleanup()

