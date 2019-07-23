checkUSB.py(python2.7/3)

program collects information regarding the dsm's data aquisition stats regarding the mount(location), Use(%), using the <df $DATAMNT/projects/$PROJECT/raw_data> command.  Program will then look at the last 10 files and collect the time stamp, then run equation to see how much longer dsm can approximately keep collecting raw_data before it fills up. 
to change to python3 switch commands.getoutout() to subprocess.getoutput(). the time stamp method also is python2x specific. 

 
Usage:
    filename.py [1] [writeToJsonPath]
    if you want to create a .log file in cwd pass in 1, or any other int to not create .log
    writeToJsonPath is the path program will output a .json file to. 
    default jsonfilepath is /tmp