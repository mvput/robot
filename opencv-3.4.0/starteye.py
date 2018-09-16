from __future__ import print_function
import sys
sys.path.append("/home/pi/luma.examples")
sys.path.append("/home/pi/luma.examples/examples")
sys.path.append("/home/pi/adafruit_python_pca9685")
sys.path.append("/home/pi/adafruit_python_pca9685/examples")
from multiprocessing import Process, Pipe
from eye import f
from simpletest import test

#!/usr/bin/env python

'''
face detection using haar cascades

USAGE:
    facedetect.py [--cascade <cascade_fn>] [--nested-cascade <cascade_fn>] [<video_source>]
'''

# Python 2/3 compatibility

import numpy as np
import cv2 as cv

# local modules
from video import create_capture
from common import clock, draw_str

def detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30),
                                     flags=cv.CASCADE_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return rects

def draw_rects(img, rects, color, width, height, parent_conn, parent_conn2, parent_ada):
    for x1, y1, x2, y2 in rects:
        cv.rectangle(img, (x1, y1), (x2, y2), color, 2)
        
        
        md_x = int((x1 + x2) / 2)
        md_y = int((y1 + y2) /2)
        
        cv.circle(img, (md_x, md_y), 5, color)
        draw_str(img, (20,20), '{} {}'.format(md_x, md_y))
        #draw_str(img, (20,20), '{} {} {} {} width: {} height: {}'.format(x1, y1, x2, y2, width, height))
        parent_conn.send((x1,y1,x2,y2))
        parent_conn2.send((x1,y1,x2,y2))
        parent_ada.send((md_x, md_y))

if __name__ == '__main__':
	parent_conn, child_conn = Pipe()
	parent_conn2, child_conn2 = Pipe()
	parent_ada, child_ada = Pipe()
	
	p = Process(target=f, args=("--display","sh1106", "--i2c-port","1", child_conn))
	p.start()
	
	x = Process(target=f, args=("--display","sh1106", "--i2c-port","0", child_conn2))
	x.start()
	
	ada = Process(target=test, args=(child_ada,))
	ada.start()
	
	parent_conn2.send((0,0,0,0))
	parent_conn.send((0,0,0,0))
	parent_ada.send((0,0,0,0))
	
	import sys, getopt
	print(__doc__)
	args, video_src = getopt.getopt(sys.argv[1:], '', ['cascade=', 'nested-cascade='])
	try:
		video_src = video_src[0]
	except:
		video_src = 0
	args = dict(args)
	cascade_fn = args.get('--cascade', "../../data/haarcascades/haarcascade_frontalface_alt.xml")
	nested_fn  = args.get('--nested-cascade', "../../data/haarcascades/haarcascade_eye.xml")
	cascade = cv.CascadeClassifier(cascade_fn)
	nested = cv.CascadeClassifier(nested_fn)
	cam = create_capture(video_src, fallback='synth:bg=../data/lena.jpg:noise=0.05')
	while True:
		ret, img = cam.read()
		gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
		gray = cv.equalizeHist(gray)
		t = clock()
		rects = detect(gray, cascade)
		vis = img.copy()
		draw_rects(vis, rects, (0, 255, 0), cam.get(3), cam.get(4), parent_conn, parent_conn2, parent_ada)
		if not nested.empty():
			for x1, y1, x2, y2 in rects:
				roi = gray[y1:y2, x1:x2]
				vis_roi = vis[y1:y2, x1:x2]
				subrects = detect(roi.copy(), nested)
				draw_rects(vis_roi, subrects, (255, 0, 0), cam.get(3), cam.get(4), parent_conn, parent_conn2, parent_ada)
		dt = clock() - t
       # draw_str(vis, (20, 20), 'time: %.1f ms' % (dt*1000))
		cv.imshow('facedetect', vis)
		if cv.waitKey(5) == 27:
			break
	cv.destroyAllWindows()
