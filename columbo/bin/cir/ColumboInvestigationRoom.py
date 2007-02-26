#!/usr/bin/python2

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: ColumboInvestigationRoom.py
#
# Author: Daniel Lemay
#
# Date: 2004-09-13
#
# CCS = Columbo Crime Scene (Each Individual PDS is a crime scene)
# CIR = Columbo Investigation Room (Investigation Room is on a LVS, clues are merged in results)
# CS  = Columbo Show (The Show is on a LVS)
#
# Description: Main file for the Columbo Project (LVS side). This program is started each 
# minute by a cron job (user pds on CIR host). Three tasks are done by this program:
# 
# 1) Obtain infos about all running PDSs (infos about clients and input directories)
# 2) Merging infos received from the PDSs
# 3) Send the merged infos to ColumboShow Host (as defined in the config. file)
#
# TO DO:
# 
# From all the infos received, I shoud create a log of all situations considered
# critical (according to definition contained in a configuration file) and send
# this log to CS host so it could be consulted.
#############################################################################################
#
# Contributor: Dominik Douville-Belanger
#
# Date: 2005-04-14
#
# Description: PX system added
#############################################################################################

"""
import sys, os, pwd, time, re, commands, itertools
sys.path.append(sys.path[0] + "/../../lib");
sys.path.append("../../lib");

from PDSPath import *                             # Contain path and filenames definitions for PDS host
from ColumboPath import *                         # Contain path and filenames definitions valuable for Columbo Programs
from PDSManager import PDSManager
from PDSClient import PDSClient
from ConfigParser import ConfigParser
from LVSManager import LVSManager
from ClientMerger import ClientMerger
from Sender import Sender
from Logger import Logger

# Specific to PX 
from CircuitMerger import CircuitMerger
from CompositeNCSCircuit import CompositeNCSCircuit
import NCSUtils

# We need to know if the CIR program will investigate about PDS or PX 
# If you want investigation about the two, start two cron jobs (one for PDS and one for PX)
system = sys.argv[1]

if system not in ['PDS', 'PX']:
    print "System is not in ['PDS', 'PX']"
    sys.exit(2)

# Read configuration file
config = ConfigParser()
config.readfp(open(FULL_MAIN_CONF)) # Configuration file MUST be there

# The following variables are identical for PDS or PX systems
ccs_user = config.get('CCS', 'user')              # User under which to send the "clues" to CIR host
ccs_host = config.get('CCS', 'host')              # CIR host where to send the "clues" to be merged
ccs_copying = config.get('CCS', 'copying')        # scp, rcp or cp for sending the "clues" to the CIR host
ccs_log_level = config.get('CCS', 'log_level')    # Level of logging for the logfile of CCS program on each PDS

user = config.get('CIR', 'user')                  # User under which to send the "results" to CS host
host = config.get('CIR', 'host')                  # CS host where to send the "results"
copying = config.get('CIR', 'copying')            # scp, rcp or cp for sending the "results" to the CS host
log_level = config.get('CIR', 'log_level')        # Level of logging for the logfile of CIR program on the LVS

if system == 'PDS':
    clues_name = config.get('CCS', 'clues_name')            # How the "clues" file will be named (path not included)
    ccs_logname = config.get('CCS', 'logname')              # Full name for the logfile of CCS program on each PDS

    results_name = config.get('CIR', 'results_name')        # How the "results" file will be named (path not included)
    logname = config.get('CIR', 'logname')                  # Full name for the logfile of CIR program on the LVS

    errorLog = config.get('CIR', 'errorLog')                # Log name of the log that will contain PDS 's errors that will be displayed by CS
    errorLogger = Logger(errorLog, log_level, "PDS_ERRORS") # Logger 

    ipvsadm_regex = config.get('CIR', 'ipvsadm_regex')      # Cluster name we search in the ipvsadm output

elif system == 'PX':
    clues_name = config.get('CCS', 'px_clues_name')         # How the "clues" file will be named (path not included)
    ccs_logname = config.get('CCS', 'px_logname')           # Full name for the logfile of CCS program on each PX

    results_name = config.get('CIR', 'px_results_name')     # How the "results" file will be named (path not included)
    logname = config.get('CIR', 'px_logname')               # Full name for the logfile of CIR program on the LVS

    errorLog = config.get('CIR', 'px_errorLog')             # Log of PX 's errors that will be displayed by CS
    errorLogger = Logger(errorLog, log_level, "PX_ERRORS")  # Logger 

    backends = config.get('CIR', 'backends').split(' ')     # Unlike PDS system which use ipvsadm, we have to define backends in conf. file
    frontend = config.get('CIR', 'frontend')                # Unlike PDS system which use ipvsadm, we have to define frontend in conf. file

    #px_groups = [tuple(group.split(',')) for group in config.get('CIR', 'px_groups').split()]  # px1,px2 px3,px4,px5 => [(px1, px2), (px3, px4, px5)]


# If not defined in configuration file, set defaults
if (not logname ):
   logname = CIR + "/log/" + "CIR.log"
if (not log_level):
   log_level = "DEBUG"

# Enable logging
logger = Logger(logname, log_level, "CIR")
logger = logger.getLogger()
logger.info("Beginning of CIR  program (%s system)" % system)

# Enable system (PDS or PX) errors logging
errorLogger = errorLogger.getLogger()

#############################################################################################
# 1) Obtain infos about all running PDSs (infos about clients and input directories)
#############################################################################################
if system == 'PDS':
    machines = LVSManager('CIR').getMachines(ipvsadm_regex)  # Get all PDS that are included in the cluster
elif system == 'PX':
    machines = backends[:]
    #machines = list(itertools.chain(*px_groups))
    if frontend:
        machines.append(frontend)

for index in range(len(machines)):
    machines[index] = machines[index].split(".")[0]  # Get only the first part of the hostname 

logger.debug("CIR program want to investigate on " + str(machines))

for machine in machines:
   print "************************************************ " + machine + " *****************************************"
   # Start the CCS Program on each PDS. After that you should have access to "clues" files
   command =  "ssh " + machine + " " + PYTHON2 + " " + CCS_PROG + " %s %s %s %s %s %s %s" % (system, clues_name, ccs_logname, ccs_log_level, ccs_copying, ccs_user, ccs_host)
   (status, output) = commands.getstatusoutput(command)
   print output
   if not status:
      logger.info("Program " + CCS_PROG + " has been run sucessfully on " +  str(machine) + " (Deduced by a good return value of ssh command by CIR)")
   else:
      logger.warning("Problem in running " +  CCS_PROG + " on " + str(machine) + " (Deduced by a bad return value of ssh command by CIR)")
      logger.error("END OF PROGRAM EXECUTION!")
      sys.exit(1)

#############################################################################################
# 2) Merging infos received from the PDSs
#############################################################################################
clues = INPUT_CLUES + "/" + clues_name     # Full path for the clues
logger.debug("Clues will be find (by CIR) in: " + clues)

if system == 'PDS':
    merger = ClientMerger(logger, errorLogger, machines)
elif system == 'PX':
    machines = backends[:]
    print("Machines are: %s" % str(machines))
    merger = CircuitMerger(logger,machines)
    wamsLogFile = open(CS + '/log/PX_WAMS.txt', 'w')

for machine in machines:
   print("Machine is: %s" % machine)
   merger.unarchiveInfos(clues + "." + machine, machine)
   #merger.printClientDict(machine)   => Debugging and exists only in ClientMerger (PDS)
   #merger.printInputDirDict(machine) => Debugging and exists only in clientMerger (PDS)

if system == 'PDS':
    merger.mergeClients()
    merger.mergeInputDirs()
elif system == 'PX':
    merger.mergeCircuit()

results_filename = RESULTS + "/" + results_name
merger.archiveResults(results_filename)
logger.debug("Results have been put by CIR in: " + results_filename)

# Creation of log files that will contain errors that will be displayed by CS
# and also of errors logs that will be used by Wams
if system == 'PDS':
    merger.logPDSErrors()
elif system == 'PX':
    merger.auditCircuit(errorLogger, errorLog, wamsLogFile) # Checks for error and log them

#############################################################################################
# 3) Send the merged infos to ColumboShow Host (as defined in the config. file)
#############################################################################################
sender = Sender('CIR') # log to 'CIR' logger
sender.send(copying, user, host, results_filename, INPUT_RESULTS)

logger.info("Ending of CIR program (system %s)" % system)
logger.info("")
#logger.removeHandler(hdlr)

#############################################################################################
# 4) Special section for PX: Do the jobs of step 2 and 3 for the frontend
#############################################################################################

if system == 'PX' and frontend:
    
    machines = [frontend.split(".")[0]]  # Only the frontend
    merger = CircuitMerger(logger, machines)

    for machine in machines:
        merger.unarchiveInfos(clues + "." + machine, machine)
    merger.mergeCircuit()
    results_filename = RESULTS + "/" + results_name + "_local"
    merger.archiveResults(results_filename)
    logger.debug("Results for the frontend (PX) have been put by CIR in: " + results_filename)
    merger.auditCircuit(errorLogger, errorLog, wamsLogFile) # Checks for error and log them

    sender = Sender('CIR') # log to 'CIR' logger
    sender.send(copying, user, host, results_filename, INPUT_RESULTS)

    logger.info("REAL Ending (frontend included) of CIR program (system %s)" % system)
    logger.info("")
