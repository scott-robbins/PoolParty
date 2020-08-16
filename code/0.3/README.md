# PoolParty_v0.3
This new architecture will build on things I've learned in the meantime, and will hopefully be cleaner and more efficient. 

### Pool Rules 
Every machine is a NODE  
 - Some nodes have higher computational power, this designates them a WORKER
 - Other nodes might be well connected on the network, they are designated the TALKER
 - Nodes that have public facing IPs will be useful for routing as network grows, so they are ROUTER

But these are simply <ROLES> a node may have (Nodes can have more than one ROLE too) and are traits about the
machine that help optimize how jobs will be schedule

========================== *Last Updated August 2020* ==========================