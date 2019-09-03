#!/usr/bin/python3
# -*- coding: utf-8 -*-

# robotController.py

from smbus import SMBus
import time,os
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

def byIR():
	global i2c
	ucB = i2c.read_byte(0x39)
	return ucB

def bySensors():
	byIr = byIR()
	
	bBR = byIr & 0x01
	bBL = (byIr >> 1) & 0x01
	bFSL = (byIr >> 2) & 0x01
	bFL = (byIr >> 3) & 0x01
	bFC = (byIr >> 4) & 0x01
	bFR = (byIr >> 5) & 0x01
	bFSR = (byIr >> 6) & 0x01
	
	return [bBR,bBL,bFSL,bFL,bFC,bFR,bFSR]

def digitalRead(nPin):
	return GPIO.input(nPin)

def vShowIR():
	global BUTTON_START
	bBR,bBL,bFSL,bFL,bFC,bFR,bFSR = bySensors()
	
	gotoxy(1,1);
	print("  { d: %d cm }            "%nUltrasonicCm() )
	print(" /----/^\\----\\");
	print(" |%c  %c %c %c  %c|"%('W' if bFSL else 'B','W' if bFL else 'B','W' if bFC else 'B','W' if bFR else 'B','W' if bFSR else 'B'))
	print("[ ]    ^    [ ]");
	print("[ ]    %c    [ ]"%('N' if digitalRead(BUTTON_START) else'P'))
	print(" |     ^     |");
	print("[ ]    ^    [ ]");
	print("[ ]    ^    [ ]");
	print(" |%c    ^    %c|"%('W' if bBL else'B','W' if bBR else 'B'))
	print(" +-----------+");

def byButton():
	global BUTTON_START
	return not digitalRead(BUTTON_START)

def gotoxy(x,y):
	print ("%c[%d;%df" % (0x1B, y, x), end='')

def nUltrasonicCm():
	global TRIG,ECHO
	
	pulse_start = time.time()
	pulse_end = time.time()
	GPIO.output(TRIG, True)                  #Set TRIG as HIGH
	time.sleep(0.00001)                      #Delay of 0.00001 seconds
	GPIO.output(TRIG, False)                 #Set TRIG as LOW
	
	while GPIO.input(ECHO)==0:               #Check whether the ECHO is LOW
		pulse_start = time.time()              #Saves the last known time of LOW pulse
	
	while GPIO.input(ECHO)==1:               #Check whether the ECHO is HIGH
		pulse_end = time.time()                #Saves the last known time of HIGH pulse 
	
	pulse_duration = pulse_end - pulse_start #Get pulse duration to a variable
	
	distance = pulse_duration * 17150        #Multiply pulse duration by 17150 to get distance
	distance = round(distance, 2)            #Round to two decimal points
	
	return distance

def analogWrite(nPin,byValue):
        global pwmBR,pwmBL,pwmFR,pwmFL
        global PWM_CONTROL_BACK_RIGHT,PWM_CONTROL_BACK_LEFT,PWM_CONTROL_FRONT_RIGHT,PWM_CONTROL_FRONT_LEFT

        if nPin == PWM_CONTROL_BACK_RIGHT:
                pwmBR.ChangeDutyCycle((int)(byValue*100)/255)
        if nPin == PWM_CONTROL_BACK_LEFT:
                pwmBL.ChangeDutyCycle((int)(byValue*100)/255)
        if nPin == PWM_CONTROL_FRONT_RIGHT:
                pwmFR.start((int)(byValue*100)/255)
        if nPin == PWM_CONTROL_FRONT_LEFT:
                pwmFL.ChangeDutyCycle((int)(byValue*100)/255)

def vMotion(nLeft, nRight): # -255 <= nLeft <= 255      -255 <= nRight <= 255
        global PWM_CONTROL_BACK_RIGHT,PWM_CONTROL_BACK_LEFT,PWM_CONTROL_FRONT_RIGHT,PWM_CONTROL_FRONT_LEFT
        global _motorStatus,i2c

        if nRight >= 0:
                analogWrite(PWM_CONTROL_FRONT_RIGHT, nRight);
                _motorStatus = (_motorStatus & (0b00111111) ) | (0x40 if (nRight != 0) else 0x00);
                analogWrite(PWM_CONTROL_BACK_RIGHT, nRight);
                _motorStatus = (_motorStatus & (0b11111100) ) | (0x02 if (nRight != 0) else 0x00);
        else:
                analogWrite(PWM_CONTROL_FRONT_RIGHT, -nRight);
                _motorStatus = (_motorStatus & (0b00111111) ) | 0x80;
                analogWrite(PWM_CONTROL_BACK_RIGHT, -nRight);
                _motorStatus = (_motorStatus & (0b11111100) ) | 0x01;
        if nLeft >= 0:
                analogWrite(PWM_CONTROL_FRONT_LEFT, nLeft);
                _motorStatus = (_motorStatus & (0b11001111) ) | (0x10 if (nLeft != 0) else 0x00);
                analogWrite(PWM_CONTROL_BACK_LEFT, nLeft);
                _motorStatus = (_motorStatus & (0b11110011) ) | (0x04 if (nLeft != 0) else 0x00);
        else:
                analogWrite(PWM_CONTROL_FRONT_LEFT, -nLeft);
                _motorStatus = (_motorStatus & (0b11001111) ) | 0x20;
                analogWrite(PWM_CONTROL_BACK_LEFT, -nLeft);
                _motorStatus = (_motorStatus & (0b11110011) ) | 0x08;

        i2c.write_byte(0x38,_motorStatus)

def vFrontRight(value, mode):
	global FORWARD,PWM_CONTROL_FRONT_RIGHT,_motorStatus,i2c
	if mode==FORWARD:
		analogWrite(PWM_CONTROL_FRONT_RIGHT, value);
		_motorStatus = (_motorStatus & (0b00111111) ) | (0x40 if (value != 0) else 0x00);
	else:
		analogWrite(PWM_CONTROL_FRONT_RIGHT, value);
		_motorStatus = (_motorStatus & (0b00111111) ) | 0x80;
	i2c.write_byte(0x38,_motorStatus)


def vFrontLeft(value, mode):
        global FORWARD,PWM_CONTROL_FRONT_LEFT,_motorStatus,i2c
        if mode==FORWARD:
                analogWrite(PWM_CONTROL_FRONT_LEFT, value);
                _motorStatus = (_motorStatus & (0b11001111) ) | (0x10 if (value != 0) else 0x00);
        else:
                analogWrite(PWM_CONTROL_FRONT_LEFT, value);
                _motorStatus = (_motorStatus & (0b11001111) ) | 0x20;
        i2c.write_byte(0x38,_motorStatus)

def vBackRight(value, mode):
        global FORWARD,PWM_CONTROL_BACK_RIGHT,_motorStatus,i2c
        if mode==FORWARD:
                analogWrite(PWM_CONTROL_BACK_RIGHT, value);
                _motorStatus = (_motorStatus & (0b11111100) ) | (0x02 if (value != 0) else 0x00);
        else:
                analogWrite(PWM_CONTROL_BACK_RIGHT, value);
                _motorStatus = (_motorStatus & (0b11111100) ) | 0x01;
        i2c.write_byte(0x38,_motorStatus)


def vBackLeft(value, mode):
        global FORWARD,PWM_CONTROL_FRONT_LEFT,_motorStatus,i2c
        if mode==FORWARD:
                analogWrite(PWM_CONTROL_BACK_LEFT, value);
                _motorStatus = (_motorStatus & (0b11110011) ) | (0x04 if (value != 0) else 0x00);
        else:
                analogWrite(PWM_CONTROL_BACK_LEFT, value);
                _motorStatus = (_motorStatus & (0b11110011) ) | 0x08;
        i2c.write_byte(0x38,_motorStatus)



def start(setup):
	global i2c,ir,BUTTON_START,TRIG,ECHO,_motorStatus
	global PWM_CONTROL_BACK_RIGHT,PWM_CONTROL_BACK_LEFT,PWM_CONTROL_FRONT_RIGHT,PWM_CONTROL_FRONT_LEFT,FORWARD,BACKWARD
	global pwmBR,pwmBL,pwmFR,pwmFL
	global disp,font,image,draw,top,bottom,fill
	BUTTON_START=17
	FORWARD = 0
	BACKWARD = 1
	os.system("clear")
	i2c = SMBus(1)
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(BUTTON_START,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	TRIG = 5                                   #Associate pin 5 to TRIG
	ECHO = 6                                   #Associate pin 6 to ECHO
	PWM_CONTROL_BACK_RIGHT = 13
	PWM_CONTROL_BACK_LEFT = 19
	PWM_CONTROL_FRONT_RIGHT = 18
	PWM_CONTROL_FRONT_LEFT = 12
	GPIO.setup(PWM_CONTROL_BACK_RIGHT ,GPIO.OUT)
	GPIO.setup(PWM_CONTROL_BACK_LEFT ,GPIO.OUT)
	GPIO.setup(PWM_CONTROL_FRONT_RIGHT ,GPIO.OUT)
	GPIO.setup(PWM_CONTROL_FRONT_LEFT ,GPIO.OUT)
	GPIO.setup(TRIG,GPIO.OUT)                  #Set pin as GPIO out
	GPIO.setup(ECHO,GPIO.IN)                   #Set pin as GPIO in
	GPIO.output(TRIG, False)                   #Set TRIG as LOW
	_motorStatus = 0
	pwmBR = GPIO.PWM(PWM_CONTROL_BACK_RIGHT , 1000)
	pwmBL = GPIO.PWM(PWM_CONTROL_BACK_LEFT , 1000)
	pwmFR = GPIO.PWM(PWM_CONTROL_FRONT_RIGHT , 1000)
	pwmFL = GPIO.PWM(PWM_CONTROL_FRONT_LEFT , 1000)
	pwmBR.start(0)
	pwmBL.start(0)
	pwmFR.start(0)
	pwmFL.start(0)
	# Raspberry Pi pin configuration:
	RST = 24
	# 128x64 display with hardware I2C:
	disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
	# Initialize library.
	disp.begin()
	# Clear display.
	disp.clear()
	disp.display()
	image = Image.new('1', (disp.width, disp.height))
	# Get drawing object to draw on image.
	draw = ImageDraw.Draw(image)
	# Draw a black filled box to clear the image.
	draw.rectangle((0,0,disp.width,disp.height), outline=0, fill=0)
	padding = -2
	top = padding
	bottom = disp.height-padding
	fill=255
	font = ImageFont.load_default()
	setup()

def vDrawText(x,y,text):
	global top, font, fill
	draw.text((x, top+y), text, font=font,fill=fill)
def vDisplay():
	global disp,image
	disp.image(image)
	disp.display()
def vDisplayClear():
	global draw,disp,width
	draw.rectangle((0,0,disp.width,disp.height), outline=0, fill=0)
	disp.display()

def main(loop):
	try:
		while True:
			loop()
	except KeyboardInterrupt:
		os.system("clear")
		print ("\nSortint ...")

