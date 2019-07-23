import unittest
import ChronyCTrackParse
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

data1 = '''Reference ID    : 2FBE24E6 (io.crash-override.org)
Stratum         : 1
Ref time (UTC)  : Tue May 28 21:01:20 2019
System time     : .00000000025 seconds slow of NTP time
Last offset     : 0.000452228 seconds
RMS offset      : 0.000304778 seconds
Frequency       : 4.094 ppm slow
Residual freq   : -0.012 ppm
Skew            : 0.167 ppm
Root delay      : 0.059771717 seconds
Root dispersion : 0.017839907 seconds
Update interval : 257.7 seconds
Leap status     : Normal'''

data2 = '''Reference ID    : 2FBE24E6 (io.crash-override.org)
Stratum         : 2
Ref time (UTC)  : Tue May 28 21:01:20 2019
System time     : -.00000000025 seconds slow of NTP time
Last offset     : 0.000452228 seconds
RMS offset      : 0.000304778 seconds
Frequency       : 4.094 ppm slow
Residual freq   : -0.012 ppm
Skew            : 0.167 ppm
Root delay      : 0.059771717 seconds
Root dispersion : 0.017839907 seconds
Update interval : 257.7 seconds
Leap status     : Normal'''

data3 = '''Reference ID    : 2FBE24E6 (io.crash-override.org)
Stratum         : 1
Ref time (UTC)  : Tue May 28 21:01:20 2019
System time     : .00000045 seconds slow of NTP time
Last offset     : 0.000452228 seconds
RMS offset      : 0.000304778 seconds
Frequency       : 4.094 ppm slow
Residual freq   : -0.012 ppm
Skew            : 0.167 ppm
Root delay      : 0.059771717 seconds
Root dispersion : 0.017839907 seconds
Update interval : 257.7 seconds
Leap status     : Normal'''

data4 = '''Reference ID    : 2FBE24E6 (io.crash-override.org)
Stratum         : 1
Ref time (UTC)  : Tue May 28 21:01:20 2019
System time     : 0 seconds slow of NTP time
Last offset     : 0.000452228 seconds
RMS offset      : 0.000304778 seconds
Frequency       : 4.094 ppm slow
Residual freq   : -0.012 ppm
Skew            : 0.167 ppm
Root delay      : 0.059771717 seconds
Root dispersion : 0.017839907 seconds
Update interval : 257.7 seconds
Leap status     : Normal'''

data5 = '''Reference ID    : 2FBE24E6 (io.crash-override.org)
Stratum         : 1
Ref time (UTC)  : Tue May 28 21:01:20 2019
System time     : 25.0 seconds slow of NTP time
Last offset     : 0.000452228 seconds
RMS offset      : 0.000304778 seconds
Frequency       : 4.094 ppm slow
Residual freq   : -0.012 ppm
Skew            : 0.167 ppm
Root delay      : 0.059771717 seconds
Root dispersion : 0.017839907 seconds
Update interval : 257.7 seconds
Leap status     : Normal'''

data6 = '''Reference ID    : 2FBE24E6 (io.crash-override.org)
Stratum         : 
Ref time (UTC)  : Tue May 28 21:01:20 2019
System time     : 
Last offset     : 0.000452228 seconds
RMS offset      : 0.000304778 seconds
Frequency       : 4.094 ppm slow
Residual freq   : -0.012 ppm
Skew            : 0.167 ppm
Root delay      : 0.059771717 seconds
Root dispersion : 0.017839907 seconds
Update interval : 257.7 seconds
Leap status     : Normal'''

class TestChronyCTrackParse(unittest.TestCase):

    def test_runEvalFunctions(self):
        t1 = ChronyCTrackParse.ChronyCTracking(data1)
        t2 = ChronyCTrackParse.ChronyCTracking(data2)
        t3 = ChronyCTrackParse.ChronyCTracking(data3)
        t4 = ChronyCTrackParse.ChronyCTracking(data4)
        t5 = ChronyCTrackParse.ChronyCTracking(data5)
        t6 = ChronyCTrackParse.ChronyCTracking(data6)

        self.assertEqual(t1.stratumAndTimeDiffCheck, True)
        self.assertEqual(t2.stratumAndTimeDiffCheck, True)
        self.assertEqual(t3.stratumAndTimeDiffCheck, False)
        self.assertEqual(t4.stratumAndTimeDiffCheck, True)
        self.assertEqual(t5.stratumAndTimeDiffCheck, False)
        self.assertEqual(t6.stratumAndTimeDiffCheck, False)
       


   
if __name__ == '__main__':
    unittest.main()
   