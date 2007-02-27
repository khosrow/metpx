"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: ColumboPaths.py
#
# Author: Daniel Lemay
#
# Date: 2004-09-08
#
# Description: Useful path under the Columbo hierarchy.
#
#############################################################################################

"""
# Useful directories
COLUMBO_HOME = "/apps/pds/tools/Columbo"                   # This line must be set correctly for any new installation
CCS = COLUMBO_HOME + "/ColumboCrimeScene"                  # Each node is a "crime scene" where clues are gathered
CIR = COLUMBO_HOME + "/ColumboInvestigationRoom"           # Here, conclusions are draw (from all the amassed clues)
CS =  COLUMBO_HOME + "/ColumboShow"                        # Presentation of results occur here
ETC = COLUMBO_HOME + "/etc"                                # General configuration
CLUES = CCS + "/clues"                                     # Clues are put there
INPUT_CLUES = CIR + "/clues"                               # Investigation receive their clues there
RESULTS = CIR + "/results"                                 # Results are put there before being sent to ColumboShow
INPUT_RESULTS = CS + "/results"                            # Show receive their results there

# Useful files
MAIN_CONF = "Columbo.conf"                                 # Main general configuration file
MAX_CONF = "maxSettings.conf"                              # Maximum and default values for clients, sources and circuits

# Useful path (directory + file)
FULL_MAIN_CONF = ETC + "/" + MAIN_CONF
FULL_MAX_CONF = ETC + "/" + MAX_CONF
CCS_PROG = CCS + "/lib/ColumboCrimeScene.py"               # Main program for CCS
CIR_PROG = CIR + "/lib/ColumboInvestigationRoom.py"        # Main program for CIR
LISTING_PROG = COLUMBO_HOME + "/lib/DirectoryLister.py"    # Used to obtain a listing used by resending tool in CS
LISTING_PROG_STARTER = CIR + "/lib/MakeMergedListing.py"   # Used to start LISTING_PROG on each appropriate machine
Q_PROG = COLUMBO_HOME + "/lib/q_gatherer.py"
