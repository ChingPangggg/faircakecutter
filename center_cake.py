import cv2
import numpy as np
import time
import subprocess
import os
import sys, pygame
from picamera import PiCamera

start = time.time()
tlim = 20
#to pitft
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')
#pygame setup
pygame.init()

size = width,height = 320,240
screen = pygame.display.set_mode(size)
white = 255, 255, 255
black = 0, 0, 0
screen.fill(black)
pygame.mouse.set_visible(False)
#big font
big_font=pygame.font.Font(None,30)
buttons = {"center the cake better on the plate": (160, 20),
	"the program will proceed when well-centered": (160,40)} #OR SAY "press button 17 when well centered" for GPIO
#GPIO setup - may not need
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
def GPIO17_callback(channel):
        global waiting
	waiting = False
GPIO.add_event_detect(17,GPIO.FALLING,callback=GPIO17_callback)

#finds circles on an image
def circles(img):
	resized_img = cv2.resize(img,(320,240))
	# convert to grayscale
	gray = cv2.cvtColor(resized_img,cv2.COLOR_BGR2GRAY)
	#img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	# blur using 3x3 kernel
	gray_blurred = cv2.blur(gray,(3,3))
	#apply hough transform on the blurred image
	detected_circles = cv2.HoughCircles(gray_blurred, cv2.HOUGH_GRADIENT, 1, 200, param1 = 50,
	               param2 = 30, minRadius = 200, maxRadius = 1000)
	x_arr = []
	y_arr = []
	r_arr = []
	# draw circles that are detected
	if detected_circles is not None:
	        # convert the circle parameters a, b, and r to integers
	        detected_circles = np.uint16(np.around(detected_circles))
		i = 0
	        for pt in detected_circles[0,:]:
			x_arr[i] = pt[0]
			y_arr[i] = pt[1]
			r_arr[i] = pt[2]
			i = i+1
	                cv2.circle(img,(pt[0],pt[1]),1,(0,0,255),3)
	                cv2.circle(img,(pt[0],pt[1]),pt[2],(0,255,0),4)
	                cv2.imshow("Detected Circle",img)
	                cv2.waitKey(0)
	return x_arr,y_arr,r_arr
j = 0
#cap = cv2.VideoCapture(0)
centered = False
waiting = True
print(j)
camera = PiCamera()
#camera.start
while ( not centered) and ( time.time() < start+tlim):
	print(j)
	j = j+1
	waiting = True
        time.sleep(0.01)
        screen.fill(black)
#	ret, pic = cap.read()
	#take picture
#	camera = PiCamera()
	camera.start_preview(alpha=255)
	time.sleep (1)
	print('take now')
	camera.capture('/home/pi/imagecake.jpg')
	camera.stop_preview()
	pic = cv2.imread('/home/pi/imagecake.jpg')
#	cv2.imshow('window', pic)
#	cv2.waitKey(0)
        #### process picture ###
	result = circles(pic)
	x_arr = result[0]
	y_arr = result[1]
	r_arr = result[2]
	#find base and cake parameters - assumes cake is second largest circle
	if len(r_arr) > 0:
		base_r = max(r_arr)
		base_ind = r_arr.index(base_r)
		base_x = x_arr.pop(base_ind)
		base_y = y_arr.pop(base_ind)
		r_arr.pop(base_ind)
		cake_r = max(r_arr)
		cake_ind = r_arr.index(cake_r)
        	cake_x = x_arr[cake_ind]
        	cake_y = y_arr[cake_ind]
		cake_error = np.sqrt((cake_x-base_x)**2 + (cake_y-base_y)**2)
		#if cake center off by >8% of plate radius (6.8 in), ask to recenter
		if cake_error > 0.08*base_r:
			for text, position in buttons.items():
			        display_text = big_font.render(text, True, white)
        			rect = display_text.get_rect(center=position)
        			screen.blit(display_text, rect)
			#uncomment to wait for user input
		#	while waiting:
		#		time.sleep(0.05)
		else:
			centered = True
			break
	else:
		display_text = big_font.render("No circles found, try again!", True, white)
		rect = display_text.get_rect(center=(160,120))
		screen.blit(display_text,rect)
	cv2.destroyAllWindows()
	pygame.display.flip()
print("Done!")
GPIO.cleanup()
#cap.release()
cv2.destroyAllWindows()

