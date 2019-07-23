import unittest
import os
import datetime
import time
import shutil
import tempfile
import logging

import checkUSB

data1 = '''Filesystem      1B-blocks     Used  Available Use% Mounted on
/dev/sda1      7804813312 79687680 7708348416   2% /media/usbdisk'''

data2 = '''Filesystem      1B-blocks     Used  Available Use% Mounted on
/dev/sda1      7804813312 79687680 7708  25% /media/usbdisk'''

data3 = '''Filesystem      1B-blocks     Used  Available Use% Mounted on
/dev/sda1      7804813312 79687680 770834   12% /media/usbdisk'''

data4 = '''Filesystem      1B-blocks     Used  Available Use% Mounted on
/dev/sda1      7804813312 79687680 50   35% /somewhere/else'''

data5 = '''Filesystem      1B-blocks     Used  Available Use% Mounted on
/dev/sda1      7804813312 79687680 7708234567   80% /media/usbdisk'''

data6 = '''Not mounted unavailable'''

#variable to represent size of test file created in bytes
sizebytes = 1500

def touch(fname, modTime):
    with open(fname, 'wb') as f:
        f.write(os.urandom(sizebytes))
    os.utime(fname, (modTime, modTime))
    #t = os.path.getmtime(fname)
    #print (datetime.datetime.fromtimestamp(t))


class TestcheckUSB(unittest.TestCase):

    def setUp(self):
        year = 2019
        month = 6
        day = 17
        hour = 16
        minute = 10
        second = 0
        datet = datetime.datetime(year=year, month=month, day=day,
                                  hour=hour, minute=minute, second=second)
        modtime = time.mktime(datet.timetuple())
        self.datadir = tempfile.mkdtemp()
        self.datafile = os.path.join(self.datadir, "s1_20190617_150000.dat")
        touch(self.datafile, modtime)
        self.testTimeStamp = datetime.datetime(2019, 6, 17, 16, 15, 0)

    def test_class(self):

        t1 = checkUSB.usbDiskParse(data1, self.datadir, self.testTimeStamp)
        t1.setTimeDelta(300)
        t1.FileSystemCheck = t1.evalFileSystem()
        t1.Status = t1.statusEval()
        t1.summary = t1.generateSummary()
        
        #t1.getAllMembers()
        #print ("sizeAvail {}".format(t1.sizeAvail))
        t2 = checkUSB.usbDiskParse(data2, self.datadir, self.testTimeStamp)
        t2.setTimeDelta(250)
        t2.FileSystemCheck = t2.evalFileSystem()
        t2.Status = t2.statusEval()
        t2.summary = t2.generateSummary()
        
        #t2.getAllMembers()
        t3 = checkUSB.usbDiskParse(data3, self.datadir, self.testTimeStamp)
        t3.setTimeDelta(300)
        t3.FileSystemCheck = t3.evalFileSystem()
        t3.Status = t3.statusEval()
        t3.summary = t3.generateSummary()
        
        #t3.getAllMembers()
        t4 = checkUSB.usbDiskParse(data4, self.datadir, self.testTimeStamp)
        t4.setTimeDelta(300)
        t4.FileSystemCheck = t4.evalFileSystem()
        t4.Status = t4.statusEval()
        t4.summary = t4.generateSummary()
        
        #t4.getAllMembers()
        t5 = checkUSB.usbDiskParse(data5, self.datadir, self.testTimeStamp)
        #t5.getAllMembers()
        t5.setTimeDelta(300)
        t5.FileSystemCheck = t5.evalFileSystem()
        t5.Status = t5.statusEval()
        t5.summary = t5.generateSummary()

        t6 = checkUSB.usbDiskParse(data6, self.datadir, self.testTimeStamp)
        t6.setTimeDelta(300)
        t6.FileSystemCheck = t6.evalFileSystem()
        t6.Status = t6.statusEval()
        t6.summary = t6.generateSummary()
        
        #t6.getAllMembers()


        #these are false becuase the time delta for filesytem check is smaller
        self.assertEqual(t1.Status, True)
        self.assertEqual(t2.Status, False)
        self.assertEqual(t3.Status, True)
        self.assertEqual(t4.Status, False)
        self.assertEqual(t5.Status, False)
        self.assertEqual(t6.Status, False)

        # #tests minLeft approximation with a delta of 5 min
        # self.assertAlmostEqual(t1.minLeft, 359866872.8, None, None, 5)
        # self.assertAlmostEqual(t2.minLeft, 359.850, None, None, 5)
        # self.assertAlmostEqual(t3.minLeft, 35986.65, None, None, 5)
        # self.assertAlmostEqual(t4.minLeft, 2.4, None, None, 5)
        # self.assertAlmostEqual(t5.minLeft, 359861557, None, None, 5)
        # self.assertAlmostEqual(t6.minLeft, 359.850, None, None, 5)

    def tearDown(self):
        if self.datadir:
            shutil.rmtree(self.datadir)

if __name__ == '__main__':

    checkUSB.log = True
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
