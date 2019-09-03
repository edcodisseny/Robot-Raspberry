from robotController import *

def setup():
	pass

def loop():
	global disp
	vDrawText(2,7,"Texto a imprimir")
	vDisplay()

start(setup)
main(loop)
