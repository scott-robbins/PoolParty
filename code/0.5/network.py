import utils
import os 
try:
	from dotenv import load_dotenv
	load_dotenv()
	NO_DOT = False
except ImportError:
	NO_DOT = True
	pass

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

def check_connected(host, ip, passwd):
	if utils.ssh_exec('whoami',ip,host,passwd,False).pop() == host:
		return True
	else:
		return False

def check_work_files(host, ip, password):
	checkCmd = 'file=/home/%s/Work/jobs.txt;[ ! -e $file ]; echo $?' % host
	return int(utils.ssh_exec(checkCmd, ip, host, password, False))

def find_missing_nodes():
	# Look at LAN for whats connected 
	# compare to MACs and find new IPs if they match
	nodes = []
	disconnected = []
	for n in get_node_names():
		nodes.append(n.split('/')[-1].split('.')[0])
	nodes = list(set(nodes)) # remove any duplicates if they exist
	node_table = {}
	old_ref = {}
	# Check which of these appear offline (because IP changed)
	for n in nodes:
		h,i,p,m = utils.load_credentials(n, False)
		old_ref[m] = [h,i,m]
		check = False
		try:
			check = check_connected(h,i,p)
		except IndexError:
			pass
		if not check:
			node_table[m] = ''
			disconnected.append(m)
		else:
			node_table[m] = [h,i]
			
	# fill node_table with new IPs for those MACs if they can be found
	node_ref = {}
	corrected = {}
	print('[*] %d Disconnected Nodes' % len(disconnected))
	if len(disconnected):
		test_scan = utils.cmd('sudo nmap -T5 -Pn 192.168.1.0/24 -p 22',False)
		current_host = ''
		for line in test_scan:
			if len(line.split(' scan report for ')) > 1:
				current_host = line.split(' report for ')[1]
				node_ref[current_host] = ''
			if len(line.split('MAC Address: '))>1:
				mac = line.split('MAC Address: ')[1].split(' ')[0]
				# node_ref[mac] = current_host 
				if mac in node_table.keys() and mac in disconnected:
					h,oi,m = old_ref[mac]
					corrected[mac] = [h,current_host]
				else:
					corrected[mac] = old_ref[mac]

	return corrected




def main():
	# Seek Potential Peers
	potential_peers = autodiscover_local()

if __name__ == '__main__':
	main()
