from robotController import *

def setup():
	global FORWARD,BACKWARD
	FORWARD = 0
	BACKWARD = 1
	pass

def loop():
	global FORWARD,BACKWARD
	vBackLeft(255, FORWARD)
	vBackRight(250, FORWARD)
	vFrontLeft(200,FORWARD)
	vFrontRight(250,FORWARD)

start(setup)
main(loop)
