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