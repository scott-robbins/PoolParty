# PoolParty_v0.3
Previous designs helped me figure out how to make pretty neat functionality for machines
controlling each others remotely (command execution, file transfer, etc.). This next version
will try and build on that foundation, and create ways to have machines work together on common
tasks. This should work better now that the fundamentals are more solid. 


### Pool Rules 
Every machine is a **node** which is given one or more of the follow <*roles*>:
---------------------------------------------------------------------------------------------
 - Some nodes have higher computational power, this designates them a **worker**
 - Other nodes might be well connected on the network, they are designated a **talker**
 - Nodes without NAT will be useful for routing as network grows, so they are **routers**
 - Nodes that store data for other notes to retrieve are **hoarders** (every node is a 
   hoarder to some degree by default)

========================== *Last Updated August 2020* ==========================