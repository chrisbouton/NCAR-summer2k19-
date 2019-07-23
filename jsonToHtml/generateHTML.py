import json
import jinja2
import sys
import os
import argparse

class jinjaRenderObj():
  def __init__(self, usb, chrony):
    self.status = dict()
    
    self.status.update(usb)
    #changes duplicate class memeber name to usbSummary, also chronyC summary
    self.status["usbSummary"] = self.status.pop("summary")
    self.status.update(chrony)
    
class populateHTMLtemplate():
  def __init__(self, dsm):
  
    self.template_dir = os.path.join(os.path.dirname(__file__), "templates")
  
    self.jinja_Env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.template_dir), autoescape = True)
 
 
    self.template = self.jinja_Env.get_template('index.html')
    
    self.outputText = self.template.render(status=dsm.status)
  
    with open("/tmp/index.html", "w") as f:
      f.write(self.outputText.encode('utf-8'))

def createParser():

  parser = argparse.ArgumentParser(description='set paths to read in  .json files.',usage="generateHTML.py checkUSBJsonPath chonrycJsonPath")
  parser.add_argument("usbJsonPath", help="the path to open/load a .json file with checkUSB class members from.", type=str)
  parser.add_argument("chronycJsonPath",help="the path to open/load .json file with chonryc class members from.", type=str)
  
  return parser

def main():
  
  parser = createParser()
  args = parser.parse_args()
  
  if(os.path.exists(args.usbJsonPath)):

    with open(args.usbJsonPath + "/USB_check.json") as f:

      usbData = json.load(f)
  else:

    usbData = None
    print("error, invalid usbcheck .json file path")

  if(os.path.exists(args.chronycJsonPath)):

    with open(args.chronycJsonPath + "/chronyc_tracking.json") as f:
      chronyData = json.load(f)
  
  else:

    chronyData = None
 
  if(usbData and chronyData is not None):
    #fill in template html page
    dsm = jinjaRenderObj(usbData, chronyData)

    x = populateHTMLtemplate(dsm)
    print("attempt to render dsm status html template success ")
    return True
  else:
    print("failed to render dsm status html template")
    return False

if __name__ == "__main__":
  main()