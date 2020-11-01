from dotenv import load_dotenv
import utils
import os 

load_dotenv()

def autodiscover_local():
	internal_addr = os.getenv('INTERNAL_IP1')
	subnet = '.'.join(internal_addr.split('.')[0:-1])+'.0/24'
	cmd = 'sudo nmap -T5 -p 22 %s' % subnet
	reporting_on = ''; current_mac = '' 
	possible_peers = []
	for line in utils.cmd(cmd, False):
		if len(line.split('Nmap scan ')) > 1:
			try:
				reporting_on = line.split('for ')[1].split(')')[0]
			except IndexError:
				print(line.split(' for '))
				pass
		if 'MAC' in line.split(' '):
			current_mac = line.split(': ')[1].split(' (')[0]
		if len(line.split('22/tcp')) > 1:
			if 'open' in line.split(' '):
				possible_peers.append([reporting_on, current_mac])
	return possible_peers

def get_node_names():
	return utils.cmd('ls PoolData/Creds/*.pem',False)


def main():
	# Seek Potential Peers
	potential_peers = autodiscover_local()

if __name__ == '__main__':
	main()
