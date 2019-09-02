from robotController import *

def setup():
	global FORWARD,BACKWARD
	FORWARD = 0
	BACKWARD = 1
	pass

def loop():
	global FORWARD,BACKWARD
	vBackLeft(255, FORWARD)
	vBackRight(100, FORWARD)
	vFrontLeft(200,FORWARD)
	vFrontRight(50,FORWARD)

start(setup)
main(loop)
