import commands
import subprocess
import json
import platform
import re
import os
from datetime import datetime, timedelta, date
import sys
import datetime
import time
import stat
import logging
import argparse

# log = False

# def writeLog(info):
#     if(log):
#         logging.info(info)

#command used in command.getoutput() to get bytesAvailableable, mount, and usage. 
class usbDiskParse:

    DFcommand = "df {} -B 1"

    #default val = None so testing is easier to pass in data
    def __init__(self,data=None, datapath=None, utctime=None):
        self.stdoutdata = data
        #testing parameters
        self.filepath = datapath
        self.utctime = utctime
    
        #bool , true if usage is below 50%, mounted, and last file mod was within 10 seconds, default False
        self.FileSystemCheck = False
        #default set to 5 seconds
        self.timeDelta = 5

        #default empty string that will be filled with class variables into human readable form
        self.summary = ""

        #bool, true if minLeft and filesystem check pass eval functions. 
        self.Status = False

        if self.filepath is None:
            self.filepath = os.path.expandvars("$DATAMNT/projects/$PROJECT/raw_data")
        if data is None:
            self.stdoutdata = commands.getoutput(self.DFcommand.format(self.filepath))

        

        #stores float of bytes availabel
        self.bytesAvailable = self._parseAvailablesize()
        
        #stores False if parse failed, string of mount location if parsed correctly. 
        self.mount = self._parseMount()
        
        #stores percentage of disk use converted to float, decimal equivalent
        self.usage = self._parseusage()
       
        #stores string
        self.hostname = self._retrieveHostName()

        #stores datetime object in UTC 
        self.timeStamp = self._getUTCtime()

        logging.info("time stamp: {}".format(self.timeStamp))
       
        #sizebytes is size in bytes from os.path.getsize("filepath/" plus last file modified"), file name is parsed 
        #to get time it was originally saved, got file from os.scandir()
        self.sizebytes, self.fileNameTime, self.fileMtimepath = self.getDirectoryAttributes()
    
        #date time since last file mod
        if self.checkLastFileMod():
            self.timeSinceFileMod = self.timeStamp - self.checkLastFileMod()
        else:
            self.timeSinceFileMod = None
        


        #calculate the estimated dateWriteRate and minutesLeft
        if self.fileNameTime is not None:
            #stores float, rate of data throughput in bytes/sec
            self.bytesPersecond = round(self.BytePerSeconds(), 3)
        
            #stores float of minutes estimated left until usb disk is out of available space. 
            #divides self.bytesAvailable by self.bytesPersecond and converts to minutes. 
            self.minLeft = self.estimateTimeLeft()
        #if last modified file time could not be parsed from filename
        else:
            self.bytesPersecond = None
            self.minLeft = None
        
        #bool, stores false if estimated min Left is less than 2 days. 
        self.minLeftCheck = self.evalDataRate()

        
        #self.Status = self.statusEval()

        #string
        #self.summary = self.generateSummary()

        
    #function to retrieve a time stamp in UTC
    def _getUTCtime(self):
        if self.utctime:
            return self.utctime
        #get current time stamp in utc
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts)
        return st
    
    #ACCESSORS
    def getMount(self):
        return self.mount
    
    def getUsage(self):
        return self.usage
    
    def getHostname(self):
        return self.hostname
    
    def gettimeStamp(self):
        return self.timeStamp

    def getFileSystemStatus(self):
        return self.FileSystemCheck

    def getTimeDelta(self):
        return self.timeDelta

    #takes in an int, in seconds, for filesystem check delta
    def setTimeDelta(self, x):
        self.timeDelta = x

    def getStatus(self):
        self.statusEval()

    def getAllMembers(self):
        print("###########################")
        print("hostname: {}".format(self.getHostname()))
        print("usage: {}".format(self.getUsage()))
        print("Mount: {}".format((self.getMount())))
        print("Timestamp: {}".format(self.gettimeStamp()))
        print("Time since last file mod: {}".format(self.timeSinceFileMod))
        print("DataWrite Rate based off last file modified(byte/second): {}".format(self.bytesPersecond))
        print("Estimated minutes left before usb fills up: {}".format(round(self.minLeft, 2)))
        print("###########################")
        if(self.getFileSystemStatus()):
            print("File system Status: Good")
        else:
            print("Status: FIle system bad")
        if(self.minLeftCheck):
            print ("minLeft check Status: Good")
        else:
            print ("minLeft check Status: Bad")
        if (self.Status):
            print("file system and minLeft approximation status check: GOOD")
        else:
            print("file system and minLeft approximation status check: BAD")
    def logAllMembers(self):
        logging.info("hostname: {}".format(self.getHostname()))
        logging.info("usage: {}".format(self.getUsage()))
        logging.info("Mount: {}".format(self.getMount()))
        logging.info("Timestamp: {}".format(self.gettimeStamp()))
        logging.info("Time since last file mod: {}".format(self.timeSinceFileMod))
        logging.info("DataWrite Rate based off last file modified(byte/second): {}".format(self.bytesPersecond))
        logging.info("Estimated minutes left before usb fills up: {}".format(round(self.minLeft, 2)))
       

    #Parsing functions

    #returns a string of the path usb is mounted to. , or None if not found
    def _parseMount(self):
        pattern = re.compile(r'(?P<use>\d+)\%\s+(?P<mount>\/.+\/.+)')
        match = pattern.search(self.stdoutdata)
        if(match is None):
            return None
        else:
            mountLocation = match.group('mount')
            mountLocation = str(mountLocation)
            return mountLocation
    
    #if parsed correctly, stores decimal equivalent of use %. 
    def _parseusage(self):
        pattern = re.compile(r'(?P<use>\d+)\%\s+(?P<mount>\/.+\/.+)')
        match = pattern.search(self.stdoutdata)
        if(match is None):
            return None
        else:
            use = match.group('use')
            use = (float(use))/100
            return use
    #stores float or -1
    def _parseAvailablesize(self):
        #pattern for regex
        pattern = re.compile(r'(?P<spaceAvail>\d+)\s*(?P<use>\d+)\%\s+(?P<mount>.*)')
        
        #search stdoutdata for regex pattern
        match = pattern.search(self.stdoutdata)

        if(match is None):
            return None
        else:
            bytesAvailable = match.group("spaceAvail")
            bytesAvailable = float(bytesAvailable)
            return bytesAvailable

    #stores string 
    def _retrieveHostName(self):
        return platform.node()

    #usage,mount,lastfileMod eval functions

    #if usage is >= 50% throw alert, if not mounted, and if timeSince last file mod greater than 10 seconds = False

    def evalFileSystem(self):
    
        if(self.usage >= .7):
            logging.info("usage >= 70%")
            return False
        elif(self.mount is None):
            logging.info("Mount error, does not equal a valid location")
            return False
        elif (self.timeSinceFileMod is None):
            return False
        elif(self.timeSinceFileMod > timedelta(seconds = self.timeDelta)):
            logging.info("time since last mod was {}, greater than 10 sec".format(self.timeSinceFileMod))
            return False
        
        logging.info("{}'s usage, Mount, and file mod check are good".format(self.getHostname()))
        return True


    #returns datetime object of last file modification
    def checkLastFileMod(self):
        if not self.fileMtimepath:
            return None
        
        t = os.path.getmtime(self.fileMtimepath)
        
        return datetime.datetime.fromtimestamp(t)
    

    #returns size of last file using os.path.getsize in bytes, and a datetime object of time parsed from filename
    # or none
    def getDirectoryAttributes(self):
        
        #pattern for regex
        pattern = re.compile(r'.*\_(?P<dateTime>\d+\_\d+)')
   
        
        #get the last modified file
        files = []
       
        #list all files and add to list
        for entry in os.listdir(self.filepath):
            #adds all files in self.filepath that end with .dat to files[]
            if entry.endswith(".dat"):
                files.append(entry)
       
        #sort list in order, so the most recent is the last index
        files.sort()
        
        if not files:
            logging.info("Error no .dat file was found in self.filepath dir")
            return None, None, None
        #search last file, the most recent, for the regex
        match = pattern.search(files[-1])

        fileMtimepath = self.filepath + '/' + files[-1]
        #get the size of the last created file
        sizebytes = os.path.getsize(fileMtimepath)
        sizebytes = int(sizebytes)
        if (match is None):
            fileCreationTime = None
        else:
            fileCreationTime = match.group("dateTime")
            #turn parsed time aspect of filename into datetime object
            fileCreationTime = datetime.datetime.strptime(fileCreationTime, "%Y%m%d_%H%M%S")
        
        return sizebytes, fileCreationTime, fileMtimepath
    
    #return float of byte/s rate
    #gets mTime of last modified file, then subtracts the time parsed from file name 
    #then converts to total seconds, and rate equals the size of the file/total elapsed seconds. 
    def BytePerSeconds(self):
        elapsedTime = self.checkLastFileMod() - self.fileNameTime
        elapsedSeconds = float(elapsedTime.total_seconds())
        
        bytePerseconds = self.sizebytes / elapsedSeconds
        #print("b/s = {}".format(bytePerseconds))
        return bytePerseconds
    
    #divides class variable "bytesAvailable by the rate to get seconds, then convert to min. 
    #returns float or none if size avail not parsed
    def estimateTimeLeft(self):
        #print ("rate = {}".format(self.bytesPersecond))
        if (self.bytesAvailable is None):
            logging.info("bytesAvailable is = to None, df command parse failed.")
            return None
        secondsLeft = self.bytesAvailable / self.bytesPersecond
        #multiply by 1 min/ 60 seconds to convert to minutes left
        minLeft = secondsLeft / 60

        minLeft = round(minLeft, 2)
        return minLeft
    
    #bool stored in class variable, status2. evals the estimated minutes left. 
    def evalDataRate(self):
        if (self.minLeft <= (24*60)):
            logging.info("Warning! estimated less than 1 day before usb disk fills up")
            return False

        elif (self.minLeft <= (48*60)):
            logging.info("Warning! estimated less than 2 days before usb disk fills up")
            return False
        
        elif(self.minLeft is None):
            logging.info("Error, program did not parse a time from last modified file name")
            return False
        
        else:
            return True
    
    #returns T/F   evaluates the class variables; status1 and 2, sets overAllStatus equal to the return
    def statusEval(self):
        if self.FileSystemCheck and self.minLeftCheck:
            logging.info("OVERALL dsm usb disk check STATUS = PASS")
            return True
        else:
            logging.info("OVERALL dsm usb disk check STATUS = FAILS")
            return False

    
#2 functions to convert python object to a dict then output to a .json file
    
    #helper function to writeToJson()
    #declares d a dict,fill it will class variables,then turn datetime objects in dict to a formatted string
    def turnDatetimeToStr(self):
        d = {}
        d.update(self.__dict__)
        #print (d)
        d['timeStamp'] = d['timeStamp'].strftime("%d-%b-%Y (%H:%M:%S.%f)")
        d['timeSinceFileMod'] = str(d['timeSinceFileMod'])
        d["fileNameTime"] = d['fileNameTime'].strftime("%d-%b-%Y (%H:%M:%S.%f)")
        del d["utctime"]
        return d


    #write json string to .jsonfile. 
    def writeToJson(self, path):
        
        if(os.path.exists(path)):

            with open(path + '/USB_check.json', 'w') as outfile:
                #serialize 1st parameter into a json formatted stream to outfile
                json.dump(self.turnDatetimeToStr(), outfile)
            #store json formatted string  into class variable jsonString
        else: 
            print("error path passed in command line does not exist")
        return (json.dumps(self.turnDatetimeToStr()))

    #returns a string filled in with important status variables in human readable format
    def generateSummary(self):
        if(self.Status):
            status = "GOOD"
        else:
            status = "BAD"
        if(self.usage is not None):
            usagePercent = self.usage * 100
        else:
            usagePercent = None
        summary = "Summary: {}'s filesystem and usb data write overall status is {} at {} has {} 1-Byte blocks available, is mounted on {}. Its usage is {}%, time difference b/w the time stamp and the last updated file's mtime is {}. The size in bytes of the file last modified is {}, the timeDelta for the file system check is {} seconds. The byte/second rate is {} and the estimated minutes left before usb disk fills up is {}.".format(self.hostname,status, self.filepath,self.bytesAvailable,self.mount,usagePercent,self.timeSinceFileMod, self.sizebytes,self.timeDelta, self.bytesPersecond, self.minLeft)

        return summary

    #main helper function to create object, configure it, then eval it.
    def runDSMstatusCheck(self, args):
        #create instance of usbDiskParse
        
        #set time delta for file system check
        self.setTimeDelta(args.fileSystemTimeDelta)

        #run the check with passed in timeDelta
        self.FileSystemCheck = self.evalFileSystem()

        #run the filesystem and minLeft check
        self.Status = self.statusEval()

        self.summary = self.generateSummary()

        self.writeToJson(args.writeToJsonPath)

        #print all important members
        self.getAllMembers()

        #log all important members only if a --log is passed in as argument
        self.logAllMembers()

#function to create argparse object
def createParser():
    parser = argparse.ArgumentParser(description='set log variable and write to json path.',usage="checkUSB.py --log writeToJsonPath fileSystemTimeDelta")
    parser.add_argument('--log', help="will set log variable to True is passed",default=False)
    parser.add_argument("writeToJsonPath", help="the path to output/dump a .json file with class members to.",default="/tmp")
    parser.add_argument("fileSystemTimeDelta", help="the time elapsed from last file mod in seconds", default=5, type=int)
    
    return parser

 


def main():

    #arg parse 
    parser = createParser()
    args = parser.parse_args()
    log = args.log  

    if log:
        #logging configuration
        logging.basicConfig(filename='usbCheckLog.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
    logging.info("############START##############")

    currDSM = usbDiskParse()
    currDSM.runDSMstatusCheck(args)
    


if __name__ == '__main__':

    main()
