from robotController import *
import subprocess

def setup():
	pass

def loop():
	global disp
	cmd = "hostname -I | cut -d\' \' -f1"
	IP=""
	while(not IP):
		IP = str(subprocess.check_output(cmd, shell = True )).replace('\'','').replace('b','').replace('n','').replace('\\','')
	vDrawText(2,7,"IP: " + IP )
	vDisplay()
	exit()

start(setup)
main(loop)
