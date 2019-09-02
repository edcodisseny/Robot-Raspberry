from robotController import *

def setup():
	pass

def loop():
	vShowIR()
	time.sleep(0.1)

start(setup)
main(loop)
