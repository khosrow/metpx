#!/usr/bin/python2

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: MakeMergedListing.py
#
# Author: Daniel Lemay
#
# Date: 2004-11-08
#
# CCS = Columbo Crime Scene (Each Individual PDS is a crime scene)
# CIR = Columbo Investigation Room (Investigation Room is on a LVS, clues are merged in results)
# CS  = Columbo Show (The Show is on a LVS)
#
# Description: Produce a merged listing of a client home directory
# 
# This program is call by the CS host (on a LVS). The program is installed an run 
# on a CIR host (a LVS). The three tasks done by this program are:
# 
# 1) Obtain infos concerning all running PDS and run the listing program on each of them
# 2) Merging infos (listing) obtained from the PDSs
# 3) Send the merged infos (listing) to ColomboShow Host
#
# Input parameters
#
# clientName: PDS client name for which we want a listing
# regex: simple regex about our search
# startDate: number of seconds since epoch
# endDate: number of second since epoch
# maxFiles: dummy
#############################################################################################

"""
import pickle
import sys, os, pwd, time, re, commands
sys.path.append(sys.path[0] + "/../../lib")
sys.path.append("../../lib")

from PDSPath import *
from ColumboPath import *
from PDSManager import PDSManager
from PDSClient import PDSClient
from ConfigParser import ConfigParser
from LVSManager import LVSManager
from ClientMerger import ClientMerger
from Sender import Sender
from Logger import Logger

DEBUG = 0
localhost = os.uname()[1]

# Read configuration file
config = ConfigParser()
config.readfp(open(FULL_MAIN_CONF))               # Config file MUST be there

ipvsadm_regex = config.get('CIR', 'ipvsadm_regex')# Cluster name we search in the ipvsadm output
user = config.get('CIR', 'user')                  # User under which to send the "results"
host = config.get('CIR', 'host')                  # Host (a CS machine) where to send the "results"
copying = config.get('CIR', 'copying')            # cp, scp or rcp
logname = config.get('CIR', 'logname')            # Full name for the logfile on CIR host
log_level = config.get('CIR', 'log_level')        # Level of logging on CIR host

ccs_user = config.get('CCS', 'user')              # User for sending "clues" (from CCS to CIR)
ccs_host = config.get('CCS', 'host')              # Host (a CIR machine) where to send the "clues" from CCS
ccs_copying = config.get('CCS', 'copying')        # cp, scp or rcp used from CCS to CIR
ccs_logname = config.get('CCS', 'logname')        # Full name for the logfile on CCS host
ccs_log_level = config.get('CCS', 'log_level')    # Level of logging on CCS host


# If not defined in configuration file, set defaults
if (not logname ):
   logname = CIS + "/log/" + "CIR.log"
if (not log_level):
   log_level = "DEBUG"

# Enable logging
logger = Logger(logname, log_level, "CIR")
logger = logger.getLogger()
logger.info("Beginning of MakeMergedListing program on " + str(localhost))

if (DEBUG):
   fichier = open ("/apps/pds/tato", "a")
   fichier.write(str(sys.argv))
   print sys.argv

# Input parameters
(clientName, regex, startDate, endDate, maxFiles) = sys.argv[1:]

#############################################################################################
# 1) Obtain infos concerning all running PDS and run the listing program on each of them
#############################################################################################
machines = LVSManager('CIR').getMachines(ipvsadm_regex)
for index in range(len(machines)):
   machines[index] = machines[index].split(".")[0]  # Get only the first part of the hostname 
logger.debug(str(machines) + "Used to create listing for a PDS client")

for machine in machines:
   command =  "ssh " + machine + " " + PYTHON2 + " " + LISTING_PROG + ' "%s" "\'%s\'" %s %s %s %s %s %s "%s" %s' % (clientName, regex, startDate, endDate, maxFiles, ccs_copying, ccs_user, ccs_host, ccs_logname, ccs_log_level)
   (status, output) = commands.getstatusoutput(command)
   if (DEBUG):
      print output  
      fichier.write(output)

   if not status:
      logger.info(command + " is OK")
   else:
      logger.warning("Problem with: " + command)

#############################################################################################
# 2) Merging infos (listing) obtained from the PDSs
#############################################################################################
bigListing = {}

def unarchiveListing(filename):
      file = open(filename, "rb")
      bigListing.update(pickle.load(file))
      file.close()

clues = INPUT_CLUES + "/" + clientName + "_listing."  

for machine in machines:
   unarchiveListing(clues + machine)

results_filename = RESULTS + "/" + clientName + "_listing"

# Archive bigListing
file = open(results_filename, "wb")
pickle.dump(bigListing, file)
file.close()

#############################################################################################
# 3) Send the merged infos (listing) to ColomboShow Host
#############################################################################################
sender = Sender('CIR')
sender.send(copying, user, host, results_filename, INPUT_RESULTS)

logger.info("Ending of MakeMergedListing program on " + str(localhost))
