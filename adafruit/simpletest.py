# Simple demo of of the PCA9685 PWM servo/LED controller library.
# This will move channel 0 from min to max position repeatedly.
# Author: Tony DiCola
# License: Public Domain
from __future__ import division
from multiprocessing import Process,Pipe
import sys
sys.path.append("/home/pi/adafruit_python_pca9685")
sys.path.append("/usr/local/lib/python3.5/dist-packages")
import threading, queue, time

from threading import Thread

# Import the PCA9685 module.
import Adafruit_PCA9685

lock = threading.Lock()
pwm = Adafruit_PCA9685.PCA9685()


def test(child_conn):
	try:
		main(child_conn)
	except KeyboardInterrupt:
		pass
		

	
def main(child_conn):
	pwm.set_pwm_freq(60)
	pwm.set_pwm(0, 0, 375)
	global previous_pos 
	previous_pos = 375
	while True:
		data = child_conn.recv()
	
		print(data)
		servo_min = 250  # Min pulse length out of 4096
		servo_max = 500  # Max pulse length out of 4096

		x = int(data[0])
		pos = 500 - 0.390625 * x 
		
	
		if x == 0:
			continue
		
		if 300 <= x <= 340:
			continue
			
		if not lock.acquire(timeout=0.1):
			continue
			
		thread = Thread(target = move_camera, args = (x, ))
		thread.start()

def move_camera(x):
	global previous_pos 
	print(int(abs(320 - x) /6))
	print(previous_pos)
			
	if x < 320:
		previous_pos	 = previous_pos + int(abs(320 - x) /6)
	else:
		previous_pos =  previous_pos - int(abs(320 - x) /6)
	print(previous_pos)
	pwm.set_pwm(0, 0, previous_pos)
	time.sleep(0.2)
		
	lock.release()
		
	
		
		
			
	
