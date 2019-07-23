Usage: 
	filename.py [checkUSBjsonFilePath] [chronycJsonFilePath]

The goal I had for this program was to open/load the json.dump files from the 
paths in the command line, combine all that data into a dict and load the
critical info from the dict, using jinja2, into an html page. 


note: user does not need to include the name of the .json file in the path., just the path to dir .json is in. 