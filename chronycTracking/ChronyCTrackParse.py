import subprocess
import sys
import re
import datetime
import platform
import logging
import json
from datetime import date
import commands
import time
import os
import argparse




class ChronyCTracking:
    #can pass in the data you want to parse from chronyc to allow better testing
    def __init__(self, data=None): 
        #CONSTRUCTOR
        if(data == None):
            #run a subprocess to get string output from command below
            self.stdoutdata = commands.getoutput("chronyc tracking")
            #print (self.stdoutdata)
        else:
            self.stdoutdata = data
        #stores an int or None if not found
        self.Stratum = self._parseStratum()

        ##stores float or None if not found
        self.sysTimeDiff = self._parseTime()

        #stores string
        self.hostname = self._retrieveHostName()

        #stores datetime obj
        self.timeStamp = self._getUTCtime()

        #stores bool
        self.stratumAndTimeDiffCheck = self.runEvalFunctions()

        #stores string of overall summary of all collected variables. 
        self.summary = self.generateSummary()

                

    def _getUTCtime(self):
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts)
        return st
    #accsessors
    def getStratum(self):
        return self.Stratum
    
    def getHostName(self):
        return self.hostname

    def getTimeDiff(self):
        return self.sysTimeDiff

    def getTimeStamp(self):
        return self.timeStamp

    #print
    def printMembers(self):
        print("hostname: {}".format(self.getHostName()))
        print("Stratum: {}".format(self.getStratum()))
        print("System Time difference: {}".format((self.getTimeDiff())))
        print("Timestamp: {}".format(self.getTimeStamp()))
        if(self.stratumAndTimeDiffCheck):
            print("stratumAndTimeDiffCheck: Good")
        else:
            print("stratumAndTimeDiffCheck: Bad")

    def logAllMembers(self):
        logging.info("hostname: {}".format(self.getHostName()))
        logging.info("Stratum: {}".format(self.getStratum()))
        logging.info("System Time difference: {}".format((self.getTimeDiff())))
        logging.info("Timestamp: {}".format(self.getTimeStamp()))
        if(self.stratumAndTimeDiffCheck):
            logging.info("stratumAndTimeDiffCheck: Good")
        else:
            logging.info("stratumAndTimeDiffCheck: Bad")
        
    #private, internal functions

    #retrieve the int value of the "Stratum" found in chronyc tracking
    #will return -1 stratum value if none found
    def _parseStratum(self):
        #parse Stratum
        pattern = re.compile(r'Stratum\s*:\s*(?P<value>\-*\d+)')
        match = pattern.search(self.stdoutdata)
        if(match == None):
            stratum = None
        else:
            stratum = match.group('value')
            stratum = int(stratum, 10)        
        return stratum
    
    #returns float value of system time in seconds
    #return -1 if not found
    def _parseTime(self):
        #parse system time from chronyc tracking command
        pattern = re.compile(r'System\stime\s*:\s*(?P<time>\-*\d*\.*\d*)\s*seconds')
        match = pattern.search(self.stdoutdata)
        if(match == None):
            timeDiff = None
        else:
            a = match.group('time')
            #evaluate gps time difference of NTP time
            timeDiff = float(a)
        return timeDiff
    
    def _retrieveHostName(self):
        return platform.node()
    

     #evaluate functions. return true if pass false if fail. 
    def evaluateStratum(self):
        #determine is stratum has a value of 1 or 2.
        if(self.Stratum != 1 and self.Stratum != 2):
            logging.info("Alert! {}'s chronyc tracking Stratum does not equal 1 or 2".format(self.hostname))
            return False
        else:
            return True

    def evaluateTimeDiff(self):
            #determine if sys time diff attribute is greater then 5 nanoseconds
            if (self.sysTimeDiff <= -.000000005 or self.sysTimeDiff >= .000000005):
                logging.info("Alert! {}'s chronyc tracking system time diff > 5 nano sec.".format(self.hostname))
                return False
            elif (self.sysTimeDiff is None):
                logging.info("Error, system time difference was not parsed correctly and value is None")
                return False
            else:
                return True

    #function to run the evaluate functions on the instance of chronyCTracking
    def runEvalFunctions(self):
    
        logging.info("########################")
        logging.info(self.timeStamp)
        logging.info("########################")
        if(self.evaluateStratum() and self.evaluateTimeDiff()):
            self.stratumAndTimeDiffCheck = True
            logging.info("{} passes chronyc tracking test\n".format(self.hostname))
            #print("{} passes chronyc tracking test\n".format(self.hostname))
            return True
        else:
            logging.info("{} fails chronyc tracking test".format(self.hostname))
            #print("{} fails chronyc tracking test".format(self.hostname))
            return False

#functions to convert python object to a dict to 

    #turn datetime object in dict to a formatted string
    def turnDatetimeToStr(self):
        d = {}
        d.update(self.__dict__)
        d['timeStamp'] = d['timeStamp'].strftime("%d-%b-%Y (%H:%M:%S.%f)")
        return d
    
    

    #write json string to text file. 
    def writeToJson(self,path):
        if(os.path.exists(path)):

            with open(path + '/chronyc_tracking.json', 'w') as outfile:

                json.dump(self.turnDatetimeToStr(), outfile)
        

    def generateSummary(self):
        
        summary = "{}'s stratum value is {}, system time offset is {}. The ChronyC tracking command was called at {}. The overall status is {}".format(self.hostname, self.Stratum, self.sysTimeDiff, self.timeStamp, self.stratumAndTimeDiffCheck)
        return summary

def createParser():
    parser = argparse.ArgumentParser(description='set LOG variable and write to json path.',usage="ChronyCTrackParse.py [--log] /writeToJsonPath")
    parser.add_argument('--log', help="will set LOG variable to True is passed",default=False)
    parser.add_argument("writeToJsonPath", help="the path to output/dump a .json file with class members to.")

    return parser

def main():
    
    #arg parse
    parser = createParser()
    args = parser.parse_args()
    log = args.log
       
        #logging configuration
    if log:
        logging.basicConfig(filename='ChronyCtracking.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
    
    logging.info("###################START##################")
    status = ChronyCTracking()
    status.writeToJson(args.writeToJsonPath)
    status.printMembers() 
    status.logAllMembers()
    

if __name__ == '__main__':
    
    main()
   




