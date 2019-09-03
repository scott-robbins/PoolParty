# PoolParty
My own DIY attempt at a small P2P kind of distributed computing system

## Distributed Computing Projects
* security camera  *(under development)*
* basic btc price analytics and monitoring *(under development)*
* distributed file system/file syncing *(under development)*

Tons of other things could be done, like using a distributed
network to run parallel cpu training with tensorflow, or a
set of nodes that parellelize tasks like scanning the internet.

My general thought here is that the way the scaling of processing
power has been heading, it seems worth exploring the idea that 
it might be more useful to buy 1 $35 Raspberry Pi every 3 months
over say the next 2 years for less than $500 than buying the best
performing laptop now for $500. Morever, I'd bet that continuing to
develop a way of generalizing tasks for a distributed network could
mean 8 Raspberry Pi's (*of course these would also scale in processing
power*) in 2 years would likely continue to outperform many laptops I 
*would be looking to buy 2 years from now*! 

* Raspberry Pi 3: 1.2 GHz CPU, 1GB RAM, 2.4 GHz Wireless

* Raspberry Pi 3B+ 1.4 GHz CPU, 1GB RAM, 2.4-5 GHz Wireless, Gigabit Ethernet   

* Raspberry Pi 4A+ 1.5 GHz CPU, 2GB RAM, 2.4-5 GHz Wireless, Gb Eth., Dual HDMI 

Utilizing the capacity of a growing fleet of Pis, for price cheaper than a 
netflix subscription, you can control an increasingly powerful network of 
machines from a cheap chromebook or laptop. Why by the next $500 beast if 
you can subscribe to Moore's Law for less than $10 a month?  

## BTC 
Still under development. Not used to making GUIs, so that's a challenge for me 
as well. Here's a snapshot of what it looks like so far: 

![btc_tracker_gui](https://raw.githubusercontent.com/scott-robbins/PoolParty/master/code/btc_ex.png)

On the left I'm watching the error in the instantaneous linear model (a new one is
started every 1000 data points). The GUI has one button to update (haven't figured out 
how to automate this because theres a lot of stuff running in background), and one to quit. 

To the right of the two buttons is a ticker showing the current date and time, and latest
btc price in USD. On the top right is a Market indicator. It will show red when the current 
price is below the moving average. If the price is above the moving average, the state 
indicator will turn green. If the price is right on the average or within an amount of tolerance
it will show blue. 

At the bottom there is a 2 Min Price Prediction, which is updated every time the model/price is 
updated with button, or by changing the setpoint (a visual guide to where you want to set a mental
record of a personal support/resistance point). 

