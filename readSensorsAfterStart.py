from robotController import *

def setup():
	while(True):
		if(byButton()):
			break

def loop():
	vShowIR()
	time.sleep(0.1)

start(setup)
main(loop)
