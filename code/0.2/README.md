## PoolParty_v0.2
This is the second version of my attempt at building a distributed computing system with python. It finally gets
to the point of being able to co-ordinate communication between the cluster but it's not very aware of network 
topology at all, and it is not very flexible or smart with generalizing for other jobs.

### Example: BTC Price Analysis
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