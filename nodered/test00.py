#!/usr/bin/python3
# -*- coding: utf-8 -*-

# robot_00.py

import paho.mqtt.client as mqtt
import re, uuid
import netifaces as ni
import time,os 
import json
import edcoRobot


def szIP(szInterficie):
	ni.ifaddresses(szInterficie)
	ip = ni.ifaddresses(szInterficie)[ni.AF_INET][0]['addr']
	return ip

def szMAC():
	# joins elements of getnode() after each 2 digits. 
	# using regex expression 
	# print ("The MAC address in formatted and less complex way is : ", end="") 
	mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
	# print (mac)
	
	return mac 


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")
    client.subscribe("ordres/")
    client.subscribe("actuadors/")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	print(msg.topic+" "+str(msg.payload))
	if msg.topic == "ordres/":
		if msg.payload == b'mac':
			# Condicionar a que el botó estigui premut
			client.publish("mac/",szMAC())
			print("publico al tema %s: %s"%("mac/",szMAC()) )
		if msg.payload == b'ip':
			# Condicionar a que el botó estigui premut
			client.publish("ip/",szIP('wlan0'))
			print("publico al tema %s: %s"%("ip/",szIP('wlan0')) )
		if msg.payload == b'sensors':
			os.system("clear")
			sensorsJS = robot.vSensors()
			client.publish("sensors/"+szMAC()+"/",sensorsJS)
	if msg.topic == "actuadors/":
		motors = json.loads(msg.payload.decode("utf-8"))
		nL, nR = motors['left'],motors['right']
		print("Left: %d  |  Right: %d"%(nL,nR))
		robot.vMotion(nL,nR)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)


szMAC()


# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
try:
	os.system("clear")
	robot = edcoRobot.EdcoRobot()
	client.loop_forever()
	
except KeyboardInterrupt:
    print ("\nSortint ...")
    robot.pwmBR.stop()
    robot.pwmBL.stop()
    robot.pwmFR.stop()
    robot.pwmFL.stop()
    client.disconnect()
    client.loop_stop()
