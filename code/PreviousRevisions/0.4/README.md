# PoolParty v0.4
The first two versions struggled because they tried to in essence reinvent SSH/SFTP, which is totally unecessary. In 0.3 I also started to figure out how to finally make the NAT traversal work for all cases, and introduced the idea of 
having a UI by running a local flask web server and rendering things in browser. 

# Current work
Before I get any further with the web frontend, I still need to improve the fundamentals of how 
the backend works. It's achieving higher transfer rates between machines now that I'm just using
ssh/sftp but the routing information is being stored far too *statically*. 

If the power goes out, I have to log back into each node and re-register them with
the main server. Improving this to have a kind of automatic rediscovery, or basically
in the client include a way to automatically reconfigure then as long as each node still has
the client I could just re-run that program if network conditions change. 

Will likely just scrap 0.4 and move to 0.5 because I think this change in philosophy represents
a minor version change in itself. Minor improvements from 0.4 will be carried over. 

=================== Last Updated October 2020 ===================
