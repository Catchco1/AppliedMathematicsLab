import numpy as np
from numpy.random import exponential
import matplotlib.pyplot as plt
from math import e
from collections import deque


def call_rate(t): # minutes between callers, on average
    if 0 <= t < 3*60:
        return(3)
    if 3*60 <= t < 6*60:
        return(3)
    if 6*60 <= t < 9*60:
        return(3)

def call_length_rate(t): # average length of calll
    if 0 <= t < 3*60:
        return(2)
    if 3*60 <= t < 6*60:
        return(2.5)
    if 6*60 <= t < 9*60:
        return(2)

# The likelihood that a caller drops the call because there are too many people ahead of them.
# This should probably be based on how long they have been waiting instead
def walkoutProb(onHoldQueueLength): 
    if(np.random.binomial(size=1, n=1, p= 1/(1+e**(-(onHoldQueueLength-6))))):
        return True
    else:
        return False

# Class for a caller
# Takes current time, previous caller, and the on hold queue as parameters
class Caller():
    def __init__(self, time, prev_caller, onHoldQueue):
        if(walkoutProb(len(onHoldQueue))):
            self.walkout = True
            self.initial_time = time
            self.done_time = time
            self.wait_time = 0
        else:
            self.walkout = False
            onHoldQueue.append(self)
            self.initial_time = time
            self.call_time = exponential(call_length_rate(time))
            if prev_caller == 'NULL':
                onHoldQueue.popleft()
                self.wait_time = 0
                self.done_time = self.initial_time + self.call_time
            else:          
                self.wait_time = max(0,prev_caller.done_time - time)
                onHoldQueue.popleft()
                self.done_time = self.initial_time + self.wait_time + self.call_time
            
        
def simulate(num=10):
    simulation = []
    for _ in range(num):
        time = exponential(call_rate(0))
        onHoldQueue = deque() 
        callers = [Caller(time,'NULL', onHoldQueue)]
        while time < 9*60:
            time += exponential(call_rate(time))
            if time < 9*60:
                caller = Caller(time,callers[-1], onHoldQueue)
                callers.append(caller)
            # otherwise, we are closed
        
        simulation.append(callers)
    return(simulation)

# dt is the time increment, width of a bin
dt = 15

wait_times = []

for i in range(int(9*60/dt)):
    wait_times.append([])

simulation = simulate(1000)
walkoutCount = 0
callerCount = 0

for record in simulation:    
    for caller in record:
        callerCount += 1
        if(caller.walkout is False):
            wait_times[int(caller.initial_time/dt)].append(caller.wait_time)
        else:
            walkoutCount += 1
print("Total callers: %d\n" % callerCount)
print("Walkout count: %d\n" % walkoutCount)

# Plot the average wait time and standard deviation for the wait time for the simulation
plt.plot([np.average(time) for time in wait_times], color = 'green')
plt.plot([np.std(time) for time in wait_times])
plt.show()


#t = np.linspace(0,16*60,num=16*6)
#
#plt.plot([customer.initial_time for customer in customers],\
#         [customer.wait_time for customer in customers])
##plt.plot(t,t**2)
##plt.plot(t,[call_rate(i) for i in t])
#
#plt.show()
#


    
