import network
import base64
import socket
import setup 
import utils
import sys 
import os 


def main():
	if '-test' not in sys.argv and 3 >len(sys.argv) > 1:
		rmt = sys.argv[1]
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((rmt, 54123))
		s.send(('UPTIME :::: Test?'))
		print(s.recv(2048))
		print(s.send('Thanks! :D'))
		s.close()

	if '-test' in sys.argv and len(sys.argv) > 3:
		api_fcn = sys.argv[2]
		rmt = sys.argv[3]
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((rmt, 54123))
		s.send(('%s :::: Test?' % api_fcn))
		print(s.recv(2048))
		s.close()


if __name__ == '__main__':
	main()
