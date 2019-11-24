# LYNX
This part of repository is a more refined subset of the tools I was hoping to develop
in order to create some kind of homegrown LAN-P2P Network (ideally to pool resources 
and complete jobs quicker, or utilize multiple nodes to run separate services that a
single application can utilize asynchronously). I've had varying degrees of success, 
mostly because designing a way to generically break tasks into a multiprocessing solution
is proving to be very much non-trivial. **However**, the ability to quickly develop a means
of communicating among the many nodes, and in a nearly autonomous way, has shown to be far
less mystifying and quite satisfying when you get it working correctly. 

So this will be a more focused sub-project to develop to tools to do the raw plumbing in
clean, fast and maybe even secure ways. 

## Challenge 1 - Key Distribution?
No need to re-invent the wheel and roll my own crypto... There's wonderful solutions that 
already exist there. I guess the hardest part in creating an architecture is getting the
implementation right, and perhaps I've still gotten it wrong, and I did my best to try and
think of something that works well but it is also using the tools that exist correctly.

*Secure Shells* are a fantastic way of communicating. The only challenge here is that you need 
each endpoint to exchange a secret to get started. This can be a challenge because each end of
the conversation needs the others secret to communicate securely, and yet they need to somehow
communicate their secret to get started. Because my endpoints are not actual clients (their 
machines I own, and presumably will be running remotely) I start by locally creating a directory
and encrypting files that contain login information for each node via SSH. 

Then using scripting I can utilize this login information and use SSH to send the directory of 
all the other nodes SSH information (already encrypted, and with the key scheme to be used going
forward) to each. While the initial step is centralized in distribution, each node is now able to
communicate with the other, so the network is **fully connected** with encrypted tunnels.

## Challenge 2 - Commands? File Distribution? 
 