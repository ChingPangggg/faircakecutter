from cakegui import num

print(num)
num = int(num)
# calculate based on calibration
# how many rotation does it make based on the

# angle for each slice is 360 deg/n
# 12 rotation of small gear = 1 overall rotation of the whole thing
# angle for each slice
numrot = 12/num
overallangle = 360/num
smallgearangle = overallangle*12 #small gear should rotate perslice

# INITIALIZE DC MOTORS
import RPi.GPIO as GPIO
import time
import os
import sys, pygame
# time.sleep(10)
# showing on piTFT
os.putenv('SDL_VIDEORIVER','fbcon')
os.putenv('SDL_FBDEV','/dev/fb0')
os.putenv('SDL_MOUSEDRV','TSLIB')
os.putenv('SDL_MOUSEDEV','/dev/input/touchscreen')

# set up screen display
pygame.init()
size = width, height = 320, 240
screen = pygame.display.set_mode(size)
size = width, height = 320, 240
screen = pygame.display.set_mode(size)
white = 255, 255, 255
black = 0, 0, 0
red = 255, 0, 0
green = 0, 255, 0
big_font = pygame.font.Font(None,40)
game_font = pygame.font.Font(None,25)
pygame.mouse.set_visible(False)

words = {"cake is cutting!": (160, 50),
	"quit": (280, 220)
}
redpanic = True
ptext = "STOP"
color = red
tlim = 60
GPIO.setmode(GPIO.BCM)
# force quit
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
def GPIO17_callback(channel):
	global running
	print("quit with bail out button")
	running = 0
	GPIO.cleanup()
# set up GPIO pins for buttons
GPIO.add_event_detect(17,GPIO.FALLING,callback=GPIO17_callback,bouncetime=400)
# set up motor pins
GPIO.setup(5, GPIO.OUT) #AI2
GPIO.setup(6, GPIO.OUT) #AI1
GPIO.setup(26, GPIO.OUT) #PWMA
GPIO.setup(13, GPIO.OUT) #pservo
#GPIO.setup(20, GPIO.OUT)
#GPIO.setup(21, GPIO.OUT)
# set output to low for both initially
GPIO.output(5,0)
GPIO.output(6,0)
pdc = GPIO.PWM(26, 100)
pdc.start(20)
#servo
servofreq = 1/(0.020 + 0.0016)
pservo = GPIO.PWM(13,servofreq)
#conversmallgearangle into dc cycle using continuous servo
redpanic = True
changed = False
dc = False
servo = False
started = False
trot = 0.88
rottime = trot*numrot
cuttime = 4
pausetime = 0.25
phase = [1,0,0,0,0,0]
pausestart = 0
cycle = 1*rottime + 2*cuttime + 3*pausetime
start = time.time()
offsettime = start
slice = 0
j = 0
print("starting to cut " + str(num) + " slices")
while time.time() < start+tlim and slice<num:
        time.sleep(0.001)
        screen.fill(black)
        display_p = big_font.render(ptext,True,white)
        p_rect = display_p.get_rect(center=(160,120))
        pygame.draw.circle(screen,color,(160,120),40)
        screen.blit(display_p,p_rect)
        for text, position in words.items():
                display_text = game_font.render(text, True, white)
                rect = display_text.get_rect(center=position)
                screen.blit(display_text, rect)
        for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                        pos = pygame.mouse.get_pos()
                        #print(pos)
                        xpos, ypos = pos
                        if p_rect.collidepoint(pos):
                                print("panic toggle")
                                redpanic = not redpanic
                        elif (xpos>260) and (ypos>200):
                                print("quitting")
                                tlim = 0
        pygame.display.flip()

        #panic button
        if redpanic:
                color = red
                ptext = "STOP"
                if changed:
			if dc:
                        	pdc.ChangeDutyCycle(20)
			elif servo:
				pservo.ChangeFrequency(1/0.0216)
				pservo.start(1.6/21.6*100)
                        changed = False
			offsettime = offsettime + time.time()-pausestart
        else:
                color = green
                ptext = "RESUME"
                if not changed:
                        pdc.stop()
			pservo.stop()
                        changed = True
			pausestart = time.time()

	if ((time.time()-offsettime) % cycle)<rottime: #servo
		servo = True
		if redpanic and phase[0] == 1:
			pservo.ChangeFrequency(1/0.0216)
			pservo.start(1.6/21.6*100)
			phase[0] = 0
			phase[1] = 1
	elif ((time.time()-offsettime) % cycle)<(rottime+pausetime): #pause
		pservo.stop()
		servo = False
       	        if redpanic and phase[1] == 1:
       	                phase[1] = 0
       	                phase[2] = 1
       	elif ((time.time()-offsettime) % cycle)<(rottime+pausetime + cuttime): #backward
		GPIO.output(5,0)
		GPIO.output(6,1)
		dc = True
		if changed:
			print(dc)
			pdc.ChangeDutyCycle(20)
       	        if redpanic and phase[2] == 1:
			pdc.start(30)
       	                phase[2] = 0
       	                phase[3] = 1
       	elif ((time.time()-offsettime) % cycle)<(rottime+2*pausetime+cuttime): #pivot left
       	        GPIO.output(5,0)
		GPIO.output(6,0)
		dc = False
       	        if redpanic and phase[3] == 1:
       	                phase[3] = 0
       	                phase[4] = 1
       	elif ((time.time()-offsettime) % cycle)<(rottime+2*pausetime+2*cuttime): #stop
		GPIO.output(6,0)
		GPIO.output(5,1)
		dc = True
       	        if redpanic and phase[4] == 1:
			pdc.start(20)
       	                phase[4] = 0
       	                phase[5] = 1
	else:
		dc = False
		GPIO.output(5,0)
		GPIO.output(6,0)
       	        if redpanic and phase[5] == 1:
                       	phase[5] = 0
                       	phase[0] = 1
			slice = slice+1
	pygame.display.flip()
print("Done!")
GPIO.cleanup()
