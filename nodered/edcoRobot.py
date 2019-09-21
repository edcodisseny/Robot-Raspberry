#!/usr/bin/python3
# -*- coding: utf-8 -*-

# edcoRobot.py

from smbus import SMBus
import time,os 
import RPi.GPIO as GPIO
import json

class EdcoRobot:
	def __init__(self):
		self.BUTTON_START = 17
		self.i2c = SMBus(1)
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.BUTTON_START,GPIO.IN,pull_up_down=GPIO.PUD_UP)
		self.TRIG = 5                                   #Associate pin 5 to TRIG
		self.ECHO = 6                                   #Associate pin 6 to ECHO
		GPIO.setup(self.TRIG,GPIO.OUT)                  #Set pin as GPIO out
		GPIO.setup(self.ECHO,GPIO.IN)                   #Set pin as GPIO in
		GPIO.output(self.TRIG, False)                   #Set TRIG as LOW		

		self.PWM_CONTROL_BACK_RIGHT = 13
		self.PWM_CONTROL_BACK_LEFT = 19
		self.PWM_CONTROL_FRONT_RIGHT = 18
		self.PWM_CONTROL_FRONT_LEFT = 12
		GPIO.setup(self.PWM_CONTROL_BACK_RIGHT ,GPIO.OUT)
		GPIO.setup(self.PWM_CONTROL_BACK_LEFT ,GPIO.OUT)
		GPIO.setup(self.PWM_CONTROL_FRONT_RIGHT ,GPIO.OUT)
		GPIO.setup(self.PWM_CONTROL_FRONT_LEFT ,GPIO.OUT)
		self._motorStatus = 0
		self.pwmBR = GPIO.PWM(self.PWM_CONTROL_BACK_RIGHT , 1000)
		self.pwmBL = GPIO.PWM(self.PWM_CONTROL_BACK_LEFT , 1000)
		self.pwmFR = GPIO.PWM(self.PWM_CONTROL_FRONT_RIGHT , 1000)
		self.pwmFL = GPIO.PWM(self.PWM_CONTROL_FRONT_LEFT , 1000)
		self.pwmBR.start(0)
		self.pwmBL.start(0)
		self.pwmFR.start(0)
		self.pwmFL.start(0)

	def byIR(self):
		return self.i2c.read_byte(0x39)

	def bySensors(self):
		byIr = self.byIR()
		
		bBR = byIr & 0x01
		bBL = (byIr >> 1) & 0x01
		bFSL = (byIr >> 2) & 0x01
		bFL = (byIr >> 3) & 0x01
		bFC = (byIr >> 4) & 0x01
		bFR = (byIr >> 5) & 0x01
		bFSR = (byIr >> 6) & 0x01
		
		return [bBR,bBL,bFSL,bFL,bFC,bFR,bFSR]

	def digitalRead(self,nPin):
		return GPIO.input(nPin)

	def vShowIR(self):
		bBR,bBL,bFSL,bFL,bFC,bFR,bFSR = self.bySensors()
		
		self.gotoxy(1,1);
		print("  { d: %d cm }            "%self.nUltrasonicCm() )
		print(" /----/^\\----\\");
		print(" |%c  %c %c %c  %c|"%('W' if bFSL else 'B','W' if bFL else 'B','W' if bFC else 'B','W' if bFR else 'B','W' if bFSR else 'B'))
		print("[ ]    ^    [ ]");
		print("[ ]    %c    [ ]"%('N' if self.digitalRead(self.BUTTON_START) else'P'))
		print(" |     ^     |");
		print("[ ]    ^    [ ]");
		print("[ ]    ^    [ ]");
		print(" |%c    ^    %c|"%('W' if bBL else'B','W' if bBR else 'B'))
		print(" +-----------+");

	def vSensors(self):
		bBR,bBL,bFSL,bFL,bFC,bFR,bFSR = self.bySensors()
		self.gotoxy(1,1);
		s = json.dumps({"us": 27,"button": "N","ir": {"bFL": "W","bCL": "W","bCC": "B","bCR": "W","bFR": "W","bL": "W","bR": "W"}}, sort_keys=True, indent=4, separators=(',', ': '))
		sensors = json.loads(s)
		sensors['us'] = self.nUltrasonicCm()
		sensors['button'] = 'N' if self.digitalRead(self.BUTTON_START) else'P'
		sensors['ir']['bFL'] = 'W' if bFSL else 'B'
		sensors['ir']['bCL'] = 'W' if bFL else 'B'
		sensors['ir']['bCC'] = 'W' if bFC else 'B'
		sensors['ir']['bCR'] = 'W' if bFR else 'B'
		sensors['ir']['bFR'] = 'W' if bFSR else 'B'
		sensors['ir']['bL'] = 'W' if bBL else 'B'
		sensors['ir']['bR'] = 'W' if bBR else 'B'
		
		szRespostaSensors = json.dumps(sensors, indent=4, sort_keys=True)
		print (szRespostaSensors)
		szRespostaSensors = json.dumps(sensors)
		return szRespostaSensors

	def gotoxy(self,x,y):
		print ("%c[%d;%df" % (0x1B, y, x), end='') 

	def nUltrasonicCm(self):
		global TRIG,ECHO
		
		GPIO.output(self.TRIG, True)                  #Set TRIG as HIGH
		time.sleep(0.00001)                      #Delay of 0.00001 seconds
		GPIO.output(self.TRIG, False)                 #Set TRIG as LOW

		while GPIO.input(self.ECHO)==0:               #Check whether the ECHO is LOW
			pulse_start = time.time()              #Saves the last known time of LOW pulse

		while GPIO.input(self.ECHO)==1:               #Check whether the ECHO is HIGH
			pulse_end = time.time()                #Saves the last known time of HIGH pulse 

		pulse_duration = pulse_end - pulse_start #Get pulse duration to a variable

		distance = pulse_duration * 17150        #Multiply pulse duration by 17150 to get distance
		distance = round(distance, 2)            #Round to two decimal points

		return distance

	def analogWrite(self,nPin,byValue):
		"""
		global pwmBR,pwmBL,pwmFR,pwmFL
		global PWM_CONTROL_BACK_RIGHT,PWM_CONTROL_BACK_LEFT,PWM_CONTROL_FRONT_RIGHT,PWM_CONTROL_FRONT_LEFT
		"""
		
		print("analogWrite (nPin = %d, byValue = %d)"%(nPin,byValue))
		
		if nPin == self.PWM_CONTROL_BACK_RIGHT:
			self.pwmBR.ChangeDutyCycle((int)(byValue*100)/255)
		if nPin == self.PWM_CONTROL_BACK_LEFT:
			self.pwmBL.ChangeDutyCycle((int)(byValue*100)/255)
		if nPin == self.PWM_CONTROL_FRONT_RIGHT:
			self.pwmFR.start((int)(byValue*100)/255)
		if nPin == self.PWM_CONTROL_FRONT_LEFT:
			self.pwmFL.ChangeDutyCycle((int)(byValue*100)/255)

	def vMotion(self,nLeft, nRight): # -255 <= nLeft <= 255      -255 <= nRight <= 255
		print("vMotion (nLeft = %d, nRight = %d)"%(nLeft,nRight))
		if nRight >= 0:
			#print("1- nFR+ vMotion (nLeft = %d, nRight = %d)"%(nLeft,nRight))
			self.analogWrite(self.PWM_CONTROL_FRONT_RIGHT, nRight);
			self._motorStatus = (self._motorStatus & (0b00111111) ) | (0x40 if (nRight != 0) else 0x00);
			#print("2- nBR+ vMotion (nLeft = %d, nRight = %d)"%(nLeft,nRight))
			self.analogWrite(self.PWM_CONTROL_BACK_RIGHT, nRight);
			#self._motorStatus = (self._motorStatus & (0b11111100) ) | (0x01 if (nRight != 0) else 0x00);
			self._motorStatus = (self._motorStatus & (0b11111100) ) | (0x02 if (nRight != 0) else 0x00);
			#print("3- nFR+ vMotion (nLeft = %d, nRight = %d)"%(nLeft,nRight))
			#print("4- nBR+ vMotion (nLeft = %d, nRight = %d)"%(nLeft,nRight))
		else:
			#print("5- nFR- vMotion (nLeft = %d, nRight = %d)"%(nLeft,nRight))
			self.analogWrite(self.PWM_CONTROL_FRONT_RIGHT, -nRight);
			self._motorStatus = (self._motorStatus & (0b00111111) ) | 0x80;
			#print("6- nBR- vMotion (nLeft = %d, nRight = %d)"%(nLeft,nRight))
			self.analogWrite(self.PWM_CONTROL_BACK_RIGHT, -nRight);
			#self._motorStatus = (self._motorStatus & (0b11111100) ) | 0x02;
			self._motorStatus = (self._motorStatus & (0b11111100) ) | 0x01;
			#print("7- nFR- vMotion (nLeft = %d, nRight = %d)"%(nLeft,nRight))
			#print("8- nBR- vMotion (nLeft = %d, nRight = %d)"%(nLeft,nRight))
		if nLeft >= 0:
			#print("9- nFL+ vMotion (nLeft = %d, nRight = %d)"%(nLeft,nRight))
			self.analogWrite(self.PWM_CONTROL_FRONT_LEFT, nLeft);
			self._motorStatus = (self._motorStatus & (0b11001111) ) | (0x10 if (nLeft != 0) else 0x00);
			#print("10-nBL+ vMotion (nLeft = %d, nRight = %d)"%(nLeft,nRight))
			self.analogWrite(self.PWM_CONTROL_BACK_LEFT, nLeft);
			#self._motorStatus = (self._motorStatus & (0b11110011) ) | (0x08 if (nLeft != 0) else 0x00);
			self._motorStatus = (self._motorStatus & (0b11110011) ) | (0x04 if (nLeft != 0) else 0x00);
			#print("11-nFL- vMotion (nLeft = %d, nRight = %d)"%(nLeft,nRight))
			#print("12-nBL- vMotion (nLeft = %d, nRight = %d)"%(nLeft,nRight))
		else:
			#print("13-nFL- vMotion (nLeft = %d, nRight = %d)"%(nLeft,nRight))
			self.analogWrite(self.PWM_CONTROL_FRONT_LEFT, -nLeft);
			self._motorStatus = (self._motorStatus & (0b11001111) ) | 0x20;
			#print("14-nBL- vMotion (nLeft = %d, nRight = %d)"%(nLeft,nRight))
			self.analogWrite(self.PWM_CONTROL_BACK_LEFT, -nLeft);
			#self._motorStatus = (self._motorStatus & (0b11110011) ) | 0x04;
			self._motorStatus = (self._motorStatus & (0b11110011) ) | 0x08;
			#print("15-nFL- vMotion (nLeft = %d, nRight = %d)"%(nLeft,nRight))
			#print("16-nBL- vMotion (nLeft = %d, nRight = %d)"%(nLeft,nRight))
			
		print("_motorStatus: 0x%X	"%self._motorStatus)
		self.i2c.write_byte(0x38,self._motorStatus)

if __name__ == "__main__":
	def main():
		os.system("clear")
		robot = EdcoRobot()
		try:
			while True:
				robot.vShowIR()
				time.sleep(0.1) 
				
		except KeyboardInterrupt:
			os.system("clear")
			print ("\nSortint ...")

	main()
