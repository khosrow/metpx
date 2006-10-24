"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: ColumboCrimeScene.py
#
# Author: Daniel Lemay
#
# Date: 2004-09-01
#
# CCS = Columbo Crime Scene (Each Individual PDS is a crime scene)
# CIR = Columbo Investigation Room (Investigation Room is on a LVS, clues are merged in results)
# CS  = Columbo Show (The Show is on a LVS)
#
# Description: Main file for the ColumboCrimeScene (CCS) software. This piece of software
# is used to collect information (about PDS clients and input directories) on a PDS machine.
# It is runned on the PDSs. The call come from the CIR host on an LVS and the clues are 
# sent to the CIR host that made the call. The main tasks are:
#
# 1) Obtain infos about the PDS on which it is running (infos about clients and input directories)
# 2) Send these infos ("clues") to CIR Host (as received in parameter)
#
# Input parameters
#  
# clues_name: filename (not the path) of the "clues" file
# logname: full name (path + filename) of the log file
# logl_level: "DEBUG" or "INFO" or etc..
# copying: type of copying (cp, rcp, scp)
# user: pds
# host: name of the CIR machine where to send the clues
#  
#############################################################################################
#
# Contributor: Dominik Douville-Belanger
#
# Date: 2005-04-14
#
# Description: PX system added
#############################################################################################
"""
import sys, os, pwd, time

print 
print "Current working directory ", os.getcwd()
print "sys.path: ", sys.path
print "Environ vars: ", os.environ.keys()
print "host: ", os.uname()[1]
print "path 0: ", sys.path[0]

sys.path.append(sys.path[0] + "/../../lib");
sys.path.append("../../lib")
print "sys.path: ", sys.path

from PDSPath import *
from ColumboPath import *
from PDSManager import PDSManager
from PDSClient import PDSClient
from Sender import Sender
from Logger import Logger

from NCSManager import NCSManager

DEBUG = 0

localhost = os.uname()[1]

system = sys.argv.pop(1)  # 'PDS' or 'PX'


def main(system):
    # Filename of the "clues", full path and filename for the log, logging level, 
    #scp or rcp, User name under which to send "clues", Machine where to send the "clues"
    (clues_name, logname, log_level, copying, user, host) = sys.argv[1:]            
    
    # Enable logging
    logger = Logger(logname, log_level, "CCS")
    logger = logger.getLogger()
    logger.info("Beginning of CCS program (system %s) on " % (system) + str(localhost))
    
    if system == 'PDS':
        # Obtain infos ("clues") from the PDS on which this software is running
        manager = PDSManager("CCS")
        manager.makeClientDict()         # Clues about PDS clients
        manager.makeInputDirDict()       # Clues about input directories
    
    elif system == 'PX':
        # Obtain infos ("clues") from the PX on which this software is running
        manager = NCSManager("CCS")
        manager.makeCircuitDict()        # Clues about PX

    # Useful printing for debugging purpose
    if (DEBUG and system == 'PDS'):
       print
       manager.printClientDict()
    
       print
       manager.printInputDirDict()
    
    # Serialization of the clues
    clues_filename = CLUES + "/" + clues_name + '.' + manager.machine
    manager.archiveInfos(clues_filename)
    
    # Sending of the clues to the CIR host
    sender = Sender('CCS')
    sender.send(copying, user, host, clues_filename, INPUT_CLUES)
    
    logger.info("Ending of CCS program (system %s) on " % (system) + str(localhost))

main(system)
