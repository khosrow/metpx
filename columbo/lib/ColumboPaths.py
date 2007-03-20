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
# Description: Useful paths under the Columbo hierarchy.
#
#############################################################################################
"""

import os.path

try:
    envVar = os.path.normpath(os.environ['COLROOT']) + '/'
except KeyError:
    envVar = '/apps/pds/tools/columbo/'


# Useful directories
ROOT = envVar
BIN = ROOT + 'bin/'                                        # executables are here
CCS = BIN +  'ccs/'                                        # ccs executable
CIR = BIN +  'cir/'                                        # cir executable
LIB = ROOT + 'lib/'                                        # main library
CS_LIB = LIB + 'cs/'                                       # cs lib
LOG = ROOT + 'log/'                                        # logs are here
CCS_LOG = LOG + 'ccs/'                                     # ccs logs
CIR_LOG = LOG + 'cir/'                                     # cir logs
CS_LOG = LOG + 'cs/'                                       # cs logs
DATA = ROOT + 'data/'                                      # all the data (clues and results)
CLUES = DATA + 'clues/'                                    # clues
RESULTS = DATA + 'results/'                                # results
ETC = ROOT + 'etc/'                                        # config files are here
WEB = ROOT + 'web/'                                        # web stuff

CLUES_WR = 'data/clues/'                                   # clues without root
RESULTS_WR = 'data/results/'                               # results without root

#CLUES = CCS + "/clues"                                     # Clues are put there
#INPUT_CLUES = CIR + "/clues"                               # Investigation receive their clues there
#RESULTS = CIR + "/results"                                 # Results are put there before being sent to ColumboShow
#INPUT_RESULTS = CS + "/results"                            # Show receive their results there

# Useful files
MAIN_CONF = "columbo.conf"                                 # Main general configuration file
MAX_CONF = "maxSettings.conf"                              # Maximum and default values for clients, sources and circuits
CIR_CONF = 'cir.conf'                                
CCS_PROG = 'ColumboCrimeScene.py'

# Useful path (directory + file)
FULL_MAIN_CONF = ETC + MAIN_CONF
FULL_MAX_CONF = ETC + MAX_CONF
FULL_CIR_CONF = ETC + CIR_CONF
SSH_EXPECT = CIR + 'sshExpect'
SSH_EXPECT_PROXY = CIR + 'sshExpectProxy'
SCP_EXPECT = CCS + 'scpExpect'
#CCS_PROG = CCS + 'ColumboCrimeScene.py'                    # Main program for CCS
CIR_PROG = CIR + 'ColumboInvestigationRoom.py'             # Main program for CIR
LISTING_PROG = LIB + 'DirectoryLister.py'                  # Used to obtain a listing used by resending tool in CS
LISTING_PROG_STARTER = CIR + 'MakeMergedListing.py'        # Used to start LISTING_PROG on each appropriate machine
