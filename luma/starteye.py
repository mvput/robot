from multiprocessing import Process, Pipe
from eye import f

if __name__ == '__main__':
	parent_conn, child_conn = Pipe()
	parent_conn2, child_conn2 = Pipe()
	
	p = Process(target=f, args=("--display","sh1106", "--i2c-port","1", child_conn))
	p.start()
	x = Process(target=f, args=("--display","sh1106", "--i2c-port","0", child_conn2))
	x.start()

	while True:
		p = input()
		parent_conn.send(p)
		parent_conn2.send(p)
