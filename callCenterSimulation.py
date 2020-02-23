import numpy as np
from numpy.random import exponential
import matplotlib.pyplot as plt
import pandas as pd
from math import e
from collections import deque
from operator import itemgetter


# def reservation_call_rate(t): # minutes between callers, on average
#     if 0 <= t < 3*60:
#         return(3)
#     if 3*60 <= t < 6*60:
#         return(3)
#     if 6*60 <= t < 9*60:
#         return(3)

def reservation_call_rate(t, df): # minutes between callers, on average
    averageCallers = df.loc[df['Time2'] <= t].iloc[-1]['Received'] / 15
    if(averageCallers == 0):
        return(1/3)
    else:
        return(1/averageCallers)

def late_call_rate(t): #prioritize these over the reservation line
    return(4.1)

def call_length_rate(t): # average length of call
    return(3)

# The likelihood that a caller drops the call because there are too many people ahead of them. This is not currently being used
def walkoutProb(onHoldQueueLength): 
    if(np.random.binomial(size=1, n=1, p= 1/(1+e**(-(onHoldQueueLength-6))))):
        return True
    else:
        return False

class Server():
    def __init__(self):
        self.busy = 0

# Class for a caller
# Takes current time, previous caller, and the on hold queue as parameters
class Caller():
    def __init__(self, time, prev_caller, serverList):
        self.initial_time = time
        self.call_time = exponential(call_length_rate(time))
        availableServer = min(serverList, key=lambda server: server.busy)
        if availableServer.busy <= time:
            self.wait_time = 0
            self.done_time = self.initial_time + self.call_time
            availableServer.busy = self.done_time
        else:
            self.wait_time = availableServer.busy - time
            self.done_time = self.initial_time + self.wait_time + self.call_time
            availableServer.busy = self.done_time
            
numServers = 15
maxTime = 3915
filename = 'FormattedData.csv'
df = pd.read_csv(filename, usecols = ['Received','estimate', 'Time2'])

def simulate(num=10):
    simulation = []
    for i in range(num):
        print(i)
        #The first caller
        time = exponential(reservation_call_rate(0, df))
        #Create a list of servers that will be answering the phones
        serverList = []
        for _ in range(numServers):
            serverList.append(Server())
        #Add the first caller to a list to keep track of all the callers in this simulation
        callers = [Caller(time,'NULL', serverList)]
        while time < maxTime:
            #Advance time only when a new caller calls in
            time += exponential(reservation_call_rate(time, df))
            if time < maxTime:
                caller = Caller(time,callers[-1], serverList)
                callers.append(caller)
            # otherwise, we are closed
        
        simulation.append(callers)
    return(simulation)

# dt is the time increment, width of a bin
dt = 15

wait_times = []
callersPer15 = []

for i in range(int(maxTime/dt)):
    wait_times.append([])
    callersPer15.append([])

simulation = simulate(1)
callerCount = 0
numCallersPerRecord = []
for record in simulation: 
    for caller in record:
        callerCount += 1
        wait_times[int(caller.initial_time/dt)].append(caller.wait_time)
        callersPer15[int(caller.initial_time/dt)].append(caller)
print("Total callers: %d\n" % callerCount)

# Plot the average wait time and standard deviation for the wait time for the simulation
ax1 = plt.subplot(3,1,1)
ax2 = plt.subplot(3,1,2)
ax3 = plt.subplot(3,1,3)
ax1.plot([np.average(len(record)) for record in callersPer15], color='red')
ax2.plot([np.average(time) for time in wait_times], color = 'green')
ax3.plot([np.std(time) for time in wait_times])
plt.show()


#t = np.linspace(0,16*60,num=16*6)
#
#plt.plot([customer.initial_time for customer in customers],\
#         [customer.wait_time for customer in customers])
##plt.plot(t,t**2)
##plt.plot(t,[reservation_call_rate(i) for i in t])
#
#plt.show()
#