ChronyCTrackParse:(Python(2.7/3))

Program starts in main function, creates object of class ChronyCTracking, then uses subprocess.getouput("chronyc tracking"), to store the output of this command into a class variable called stdoutdata, next class variables Stratum, hostname, sysTimeDiff(System time: x)in chronyc, nand timeStamp are collected through functions called in constructor. The Program then evaluates the collected chronyc tracking attributes and gives a pass or fail status on the object. 
**for python3 change commands.getoutput("chronyc tracking") to subprocess.getouput("chro...")

Usage:
    python filename.py [1] [writeToJsonPath]
    pass in a [1] to create a .log file, or any other int to not
    writeToJsonPath = the path to output/json.dump the .json file to which contains all the class varibale 