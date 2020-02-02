import numpy as np
from numpy.random import exponential
import matplotlib.pyplot as plt
from math import e
from collections import deque


def arrival_rate(t): # minutes between customers, on average
    if 0 <= t < 4*60:
        return(1)
    if 4*60 <= t < 11*60:
        return(2)
    if 11*60 <= t < 16*60:
        return(3)

def counter_rate(t): # minutes to place an order, on average
    if 0 <= t < 4*60:
        return(2/3)
    if 4*60 <= t < 11*60:
        return(1)
    if 11*60 <= t < 16*60:
        return(1.25)

def preparation_rate(t): # minutes to make a drink, on average
    if 0 <= t < 4*60:
        return(0.75)
    if 4*60 <= t < 11*60:
        return(1.2)
    if 11*60 <= t < 16*60:
        return(1.5)

def walkoutProb(lineLength):
    if(np.random.binomial(size=1, n=1, p= 1/(1+e**(-(lineLength-6))))):
        return True
    else:
        return False

def downorderProb(lineLength):
    if(np.random.binomial(size=1, n=1, p= 1/(1+e**(-(lineLength-5))))):
        return True
    else:
        return False


class Customer():
    def __init__(self, time, prev_customer, counterLine, drinkLine):
        if(walkoutProb(len(counterLine))):
            self.walkout = True
            self.downOrder = False
            self.arrival_time = time
            self.counter_time = 0
            self.done_order_time = 0
            self.prep_time = 0
            self.done_time = time
            self.in_line_time = 0
            self.wait_time = 0
        else:
            self.walkout = False
            counterLine.append(self)
            self.arrival_time = time
            self.counter_time = exponential(counter_rate(time))
            if(downorderProb(len(drinkLine))):
                self.downOrder = True
            else:
                self.downOrder = False
            drinkLine.append(self)
            self.prep_time = exponential(preparation_rate(time))
            if prev_customer == 'NULL':
                self.done_order_time = time + self.counter_time
                counterLine.popleft()
                self.done_time = self.done_order_time + self.prep_time
                drinkLine.popleft()
            else:          
                self.done_order_time = max(time,prev_customer.done_order_time)+\
                                    self.counter_time
                counterLine.popleft()
                self.done_time = max(self.done_order_time,prev_customer.done_time)+\
                                self.prep_time
                drinkLine.popleft()
            self.in_line_time = self.done_order_time - self.arrival_time
            self.wait_time = self.done_time - self.done_order_time
            
        
def simulate(num=10):
    simulation = []
    for i in range(num):
        time = exponential(arrival_rate(0))
        counterLine = deque() 
        drinkLine = deque()
        customers = [Customer(time,'NULL', counterLine, drinkLine)]
        while time < 16*60:
            time += exponential(arrival_rate(time))
            if time < 16*60:
                customer = Customer(time,customers[-1], counterLine, drinkLine)
                customers.append(customer)
            # otherwise, we are closed
        
        simulation.append(customers)
    return(simulation)

# dt is the time increment, width of a bin
dt = 10

in_line_times = []
wait_times = []

for i in range(int(16*60/dt)):
    in_line_times.append([])
    wait_times.append([])

simulation = simulate(1000)
morningLaborCost = (15*(1/counter_rate(0)) + 20*(1/preparation_rate(0))) * 4
dayLaborCost = (15*(1/counter_rate(4*60)) + 20*(1/preparation_rate(4*60))) * 7
eveningLaborCost = (15*(1/counter_rate(11*60)) + 20 *(1/preparation_rate(11*60))) * 5
totalLaborCost = morningLaborCost + dayLaborCost + eveningLaborCost
downOrderCost = 0
walkoutCost = 0

for record in simulation:    
    for customer in record:
        if(customer.walkout is False):
            in_line_times[int(customer.arrival_time/dt)].append(customer.in_line_time)
            wait_times[int(customer.arrival_time/dt)].append(customer.wait_time)
            if(customer.downOrder):
                downOrderCost += 1
        else:
            walkoutCost += 2
downOrderCost = downOrderCost / len(simulation)
walkoutCost = walkoutCost / len(simulation)
totalCost = downOrderCost + walkoutCost + morningLaborCost + dayLaborCost + eveningLaborCost
print("Average down order cost per day: %d\n \
    Walkout cost: %d\n \
    Labor cost: %d\n\
    Total average cost per day: %d" % (downOrderCost, walkoutCost, totalLaborCost, totalCost))
plt.plot([np.average(time) for time in in_line_times])
plt.plot([np.std(time) for time in in_line_times])
plt.show()


#t = np.linspace(0,16*60,num=16*6)
#
#plt.plot([customer.arrival_time for customer in customers],\
#         [customer.wait_time for customer in customers])
##plt.plot(t,t**2)
##plt.plot(t,[arrival_rate(i) for i in t])
#
#plt.show()
#


    
