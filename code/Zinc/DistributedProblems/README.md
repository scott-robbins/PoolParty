# Distributed Problems 
This project contains utilities and assorted code to kind of fill out a loose API
for conducting peer to peer actions and fundamental network computing operations
such as file transfer, command execution, etc. 

Here's an example of using these utilities to send a remote host a song, convert
it it a WAV, and play it on remote machine (in ~3 lines).
```
$ cp ../P2P/Shared/Vulfpeck/wait_for_the_moment.mp3 $PWD;  # copy song to local directory
$ python utils.py send 192.168.1.217 wait_for_the_moment.mp3; # send it to remote host
$ python utils.py cmd 192.168.1.217 'ffmpeg -i wait_for_the_moment.mp3 wait.wav; aplay wait.wav';
# ^ Play it at the other end, after converting to a WAV with FFMpeg. 
```

