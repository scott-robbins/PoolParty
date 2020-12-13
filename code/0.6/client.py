import network
import base64
import socket
import setup 
import utils
import sys 
import os 


def main():
	if len(sys.argv) > 1:
		rmt = sys.argv[1]
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((rmt, 54123))
		s.send(('UPTIME :::: Test?'))
		print(s.recv(2048))
		s.close()


if __name__ == '__main__':
	main()
