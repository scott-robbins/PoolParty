# PoolParty - v0.6
In 0.5 I learned some more good things about what works and a few more things about what doesn't. 

What *did* work:
* continue checking if all nodes are present and make note when a node appears offline
* Using MACs to figure out when a node has a new IP
* file distribution. Although it never stopped and if any files got deleted they would be 	
  automatically sent again. 


What *doesn't* work: 
* Making **all** of the API stuff use encryption is messing things up, and it really might be 	
  overkill for this project. I'm going to avoid that for now and just keep moving. 
* Forcing all of the code to python 3 is a bad because all of the nodes need to be up to date on 
  python 3 in that case. But the nodes might not really have a lot of maintenance going on so that's a bad idea.


## Design 

## Example Tasks
How much faster could one quickly port scan the entire internet (saving result) with a few nodes versus one computer? 

[1] Break up Job into pieces 
	- distribute IP Address Space
	- determine when to log/save results

[2] When nodes come online give them their job
	- Node is told to start running a task
	- node.py should add Work, and Status files to track job 

[3] Take note a node confirms the job they've been given
	- Status variable for that program is upated

[4] Master machine waits for machines to signal they have finished work


[5] Log changes in status/work after transmitting result of work 

[6] 

[7]

================     **Last Updated ** *12/26/2020*     ================