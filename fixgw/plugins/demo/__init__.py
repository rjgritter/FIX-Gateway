#!/usr/bin/env python

#  Copyright (c) 2019 Phil Birkelbach
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
#  USA.import plugin

#  This is a simple data simulation plugin.  It's mainly for demo purposese
#  It really has no function other than simple testing of displays

# TODO Make the keylist configurable
# TODO add some functions to change the values (noise, cyclic, reduction, etc)

import threading
import time
from collections import OrderedDict
import fixgw.plugin as plugin

class MainThread(threading.Thread):
    def __init__(self, parent):
        super(MainThread, self).__init__()
        self.getout = False   # indicator for when to stop
        self.parent = parent  # parent plugin object
        self.log = parent.log  # simplifies logging
        self.keylist = {"ROLL":3, "PITCH":0, "IAS":113, "ALT":4220,
                        "TACH1":3000, "MAP1":30.0, "FUELP1":28.5, "OILP1":125.0,
                        "OILT1":100, "FUELQ1":11.2, "FUELQ2":19.8, "OAT": 32,
                        "CHT11":201,"CHT12":202,"CHT13":199,"CHT14":200,
                        "EGT11":710,"EGT12":700,"EGT13":704,"EGT14":702,
                        "FUELF1":8.7,"VOLT":13.7,"CURRNT":45.6
                        }
        # self.keylist = {"TACH1":2450}
        # Initialize the points
        for each in self.keylist:
            self.parent.db_write(each, self.keylist[each])

    def run(self):
        counter = 0
        increasing = True

        while not self.getout:
            time.sleep(0.03)
            # We just read the point and write it back in to reset the TOL timer
            for each in self.keylist:
                # x = self.parent.db_read(each)
                # self.parent.db_write(each, x)

                min = 0
                max = self.keylist[each]
                range = max - min
                x = min + (range * counter / 100)
                self.parent.db_write(each, x)
                
            # min = 0
            # max = 3000
            # range = max - min
            # x = min + (range * counter / 100)

            # key = {"TACH1":x}
            # self.parent.db_write("TACH1", x)

            if increasing:
                counter += 1
                if counter >= 100:
                    increasing = False
            else:
                counter -= 1
                if counter <= 0:
                    increasing = True


        self.running = False

    def stop(self):
        self.getout = True


class Plugin(plugin.PluginBase):
    def __init__(self, name, config):
        super(Plugin, self).__init__(name, config)
        self.thread = MainThread(self)
        self.status = OrderedDict()

    def run(self):

        self.thread.start()

    def stop(self):
        self.thread.stop()
        if self.thread.is_alive():
            self.thread.join(1.0)
        if self.thread.is_alive():
            raise plugin.PluginFail

    def get_status(self):
        return self.status
