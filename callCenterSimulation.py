import numpy as np
from numpy.random import exponential
import matplotlib.pyplot as plt
import pandas as pd
import csv
from math import e
from collections import deque
from operator import itemgetter

def reservation_call_rate(t, df): # minutes between callers, on average
    averageCallers = df.loc[df['Time2'] <= t].iloc[-1]['Received'] / 15
    if(averageCallers == 0):
        return(15)
    else:
        return(1/averageCallers)

def call_length_rate(t): # average length of call
    return(3)

def late_call_length_rate(t):
    return(4.1)


# The likelihood that a caller drops the call because there are too many people ahead of them. This is not currently being used
# def walkoutProb(onHoldQueueLength): 
#     if(np.random.binomial(size=1, n=1, p= 1/(1+e**(-(onHoldQueueLength-6))))):
#         return True
#     else:
#         return False

def assignReservationServerStations(t, df):
    return df.loc[df['Time2'] <= t].iloc[-1]['estimate']

def assignLateServerStations(t, df):
    return df.loc[df['Time2'] <= t].iloc[-1]['optimized']

class Server():
    def __init__(self, station):
        self.workingUntil = 0
        self.stationNumber = station

# Class for a caller
# Takes current time, previous caller, and the on hold queue as parameters
class Caller():
    def __init__(self, time, prev_caller, serverList, numAvailableServerStations):
        self.initial_time = time
        self.call_time = exponential(call_length_rate(time))
        workingServers = filter(lambda server: server.stationNumber <= numAvailableServerStations, serverList)
        bestServer = min(workingServers, key=lambda server: server.workingUntil)
        if bestServer.workingUntil <= time:
            self.wait_time = 0
            self.done_time = self.initial_time + self.call_time
            bestServer.workingUntil = self.done_time
        else:
            self.wait_time = bestServer.workingUntil - time
            self.done_time = self.initial_time + self.wait_time + self.call_time
            bestServer.workingUntil = self.done_time
        if(self.wait_time < 0.167):
            self.wait_class = 0
        elif(self.wait_time < 2):
            self.wait_class = 1
        elif(self.wait_time < 3):
            self.wait_class = 2
        elif(self.wait_time < 5):
            self.wait_class = 3
        else:
            self.wait_class = 4
            
filename = 'FormattedData2.csv'
df = pd.read_csv(filename, usecols = ['Received','estimate', 'Time2', 'X0.10sec', 'X11.120sec', 'X2.3min', 'X3.5min', 'Over_5min'])
maxServerStations = int(max(df['estimate']))
maxTime = int(max(df['Time2']))
numSimulations = 20
print(maxServerStations)

def simulate(num=10):
    simulation = []
    for i in range(num):
        print(i)
        #The first caller
        time = exponential(reservation_call_rate(0, df))
        #Create a list of servers that will be answering the phones
        serverList = []
        for j in range(maxServerStations):
            serverList.append(Server(j))
        #Add the first caller to a list to keep track of all the callers in this simulation
        numAvailableServerStations = assignReservationServerStations(time, df)
        callers = [Caller(time,'NULL', serverList, numAvailableServerStations)]
        while time < maxTime:
            #Advance time only when a new caller calls in
            time += exponential(reservation_call_rate(time, df))
            if time < maxTime:
                numAvailableServerStations = assignReservationServerStations(time, df)
                caller = Caller(time,callers[-1], serverList, numAvailableServerStations)
                callers.append(caller)
        
        simulation.append(callers)
    return(simulation)

# dt is the time increment, width of a bin
dt = 15

wait_times = []
callersPer15 = []
averageWaitTimes = [0,0,0,0,0]
waitTimesPer15 = []
absoluteValueDifference = []
lessThanTenSecs = []
tenSecSD = []
lessThanTwoMin = []
twoMinSD = []
lessThanThreeMin = []
threeMinSD = []
lessThanFiveMin = []
fiveMinSD = []
greaterThanFiveMin = []
greaterThanFiveMinSD = []
waitClasses = []

for i in range(int(maxTime/dt)):
    wait_times.append([])
    callersPer15.append([])
    waitTimesPer15.append([0,0,0,0,0])
    absoluteValueDifference.append([0,0,0,0,0,0])
    waitClasses.append([])
    lessThanTenSecs.append([])
    tenSecSD.append(0)
    lessThanTwoMin.append([])
    twoMinSD.append(0)
    lessThanThreeMin.append([])
    threeMinSD.append(0)
    lessThanFiveMin.append([])
    fiveMinSD.append(0)
    greaterThanFiveMin.append([])
    greaterThanFiveMinSD.append(0)

simulation = simulate(numSimulations)
callerCount = 0
for record in simulation: 
    for caller in record:
        callerCount += 1
        wait_times[int(caller.initial_time/dt)].append(caller.wait_time)
        callersPer15[int(caller.initial_time/dt)].append(caller)
        waitClasses[int(caller.initial_time/dt)].append(caller.wait_class)
        if caller.wait_time <= 0.167:
            averageWaitTimes[0] += 1
            waitTimesPer15[int(caller.initial_time/dt)][0] += 1
        elif caller.wait_time <= 2:
            averageWaitTimes[1] += 1
            waitTimesPer15[int(caller.initial_time/dt)][1] += 1
        elif caller.wait_time <= 3:
            averageWaitTimes[2] += 1
            waitTimesPer15[int(caller.initial_time/dt)][2] += 1
        elif caller.wait_time <= 5:
            averageWaitTimes[3] += 1
            waitTimesPer15[int(caller.initial_time/dt)][3] += 1
        else:
            averageWaitTimes[4] += 1
            waitTimesPer15[int(caller.initial_time/dt)][4] += 1
    for index,interval in enumerate(waitClasses):
        if(len(callersPer15[index]) == 0):
            lessThanTenSecs[index].append(0)
        else:
            lessThanTenSecs[index].append((interval.count(0) / len(callersPer15[index])) * 100)
            lessThanTwoMin[index].append((interval.count(1) / len(callersPer15[index])) * 100)
            lessThanThreeMin[index].append((interval.count(2) / len(callersPer15[index])) * 100)
            lessThanFiveMin[index].append((interval.count(3) / len(callersPer15[index])) * 100)
            greaterThanFiveMin[index].append((interval.count(4) / len(callersPer15[index])) * 100)
print("Total callers: %d\n" % callerCount)

for index,interval in enumerate(lessThanTenSecs):
    sd = np.std(interval)
    avg = np.average(interval)
    if(df['X0.10sec'][index] >= (avg - sd) and df['X0.10sec'][index] <= (avg + sd)):
        tenSecSD[index] = 1
for index,interval in enumerate(lessThanTwoMin):
    sd = np.std(interval)
    avg = np.average(interval)
    if(df['X11.120sec'][index] >= (avg - sd) and df['X11.120sec'][index] <= (avg + sd)):
        twoMinSD[index] = 1
for index,interval in enumerate(lessThanThreeMin):
    sd = np.std(interval)
    avg = np.average(interval)
    if(df['X2.3min'][index] >= (avg - sd) and df['X2.3min'][index] <= (avg + sd)):
        threeMinSD[index] = 1
for index,interval in enumerate(lessThanFiveMin):
    sd = np.std(interval)
    avg = np.average(interval)
    if(df['X3.5min'][index] >= (avg - sd) and df['X3.5min'][index] <= (avg + sd)):
        fiveMinSD[index] = 1
for index,interval in enumerate(greaterThanFiveMin):
    sd = np.std(interval)
    avg = np.average(interval)
    if(df['Over_5min'][index] >= (avg - sd) and df['Over_5min'][index] <= (avg + sd)):
        greaterThanFiveMinSD[index] = 1

standardDeviationResults = [list(row) for row in zip(tenSecSD, twoMinSD, threeMinSD, fiveMinSD, greaterThanFiveMinSD)]

loopCount = 0
for entry in absoluteValueDifference:
    for i in range(5):
        if i == 0: 
            if(len(callersPer15[loopCount]) == 0):
                entry[i] = abs(0 - df['X0.10sec'][loopCount])
            else:
                entry[i] = abs(waitTimesPer15[loopCount][i]/ len(callersPer15[loopCount]) * 100 - df['X0.10sec'][loopCount])
        elif i == 1:
            if(len(callersPer15[loopCount]) == 0):
                entry[i] = abs(0 - df['X11.120sec'][loopCount])
            else:
                entry[i] = abs(waitTimesPer15[loopCount][i]/ len(callersPer15[loopCount]) * 100 - df['X11.120sec'][loopCount])
        elif i == 2:
            if(len(callersPer15[loopCount]) == 0):
                entry[i] = abs(0 - df['X2.3min'][loopCount])
            else:
                entry[i] = abs(waitTimesPer15[loopCount][i]/ len(callersPer15[loopCount]) * 100 - df['X2.3min'][loopCount])
        elif i == 3:
            if(len(callersPer15[loopCount]) == 0):
                entry[i] = abs(0 - df['X3.5min'][loopCount])
            else:
                entry[i] = abs(waitTimesPer15[loopCount][i]/ len(callersPer15[loopCount]) * 100 - df['X3.5min'][loopCount])
        elif i == 4:
            if(len(callersPer15[loopCount]) == 0):
                entry[i] = abs(0 - df['Over_5min'][loopCount])
            else:
                entry[i] = abs(waitTimesPer15[loopCount][i]/ len(callersPer15[loopCount]) * 100 - df['Over_5min'][loopCount])
        entry[5] += entry[i]
    loopCount += 1

absoluteValueDifference.insert(0,['<10 seconds', '<2 minutes', '<3 minutes', '<5 minutes', '>5 minutes', 'Total difference'])
with open('absoluteDifferenceOutput.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(absoluteValueDifference)

standardDeviationResults.insert(0,['<10 seconds', '<2 minutes', '<3 minutes', '<5 minutes', '>5 minutes'])
with open('standardDeviationOutput.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(standardDeviationResults)

loopCount = 0
for entry in waitTimesPer15:
    for i in range(len(entry)):
        if(len(callersPer15[loopCount]) == 0):
            entry[i] = 0
        else:
            entry[i] = entry[i] / len(callersPer15[loopCount]) * 100
    loopCount += 1
waitTimesPer15.insert(0,['<10 seconds', '<2 minutes', '<3 minutes', '<5 minutes', '>5 minutes'])
with open('output.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(waitTimesPer15)


# Bar Chart construction
barChartBins = ('<10 seconds', '<2 minutes', '<3 minutes', '<5 minutes', '>5 minutes')
y_pos = np.arange(len(barChartBins))
averageWaitTimes = [waitTime / callerCount for waitTime in averageWaitTimes]

# Plot the average wait time and standard deviation for the wait time for the simulation
# fig, axs =  plt.subplots(nrows=5, ncols=1)
# axs[0] = plt.subplot(5,1,1)
# axs[1] = plt.subplot(5,1,2)
# axs[2] = plt.subplot(5,1,3)
# axs[3] = plt.subplot(5,1,4)
# axs[4] = plt.subplot(5,1,5)

# axs[0].plot([len(record)/numSimulations for record in callersPer15], color='red')
# axs[1].plot([np.average(time) for time in wait_times], color = 'green')
# axs[2].plot([np.std(time) for time in wait_times])
# axs[3].plot([np.average(station) for station in df['estimate']], color = 'brown')
# axs[4].bar(barChartBins, averageWaitTimes)

# axs[0].title.set_text('Average Number of Callers')
# axs[1].title.set_text('Average Wait Time')
# axs[2].title.set_text('Standard Deviation of Wait Time')
# axs[3].title.set_text('Average Number of Servers')
# axs[4].title.set_text('Percentage of Callers with Specified Wait Times')
plt.figure().suptitle('Average Number of Callers')
plt.plot([len(record)/numSimulations for record in callersPer15], color='red')
plt.figure().suptitle('Average Wait Time')
plt.plot([np.average(time) for time in wait_times], color = 'green')
plt.figure().suptitle('Standard Deviation of Wait Time')
plt.plot([np.std(time) for time in wait_times])
plt.figure().suptitle('Average Number of Servers')
plt.plot([np.average(station) for station in df['estimate']], color = 'brown')
plt.figure().suptitle('Percentage of Callers with Specified Wait Times')
plt.bar(barChartBins, averageWaitTimes)
# fig.tight_layout()

plt.show()