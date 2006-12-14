"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: PDSPath.py
#
# Author: Daniel Lemay
#
# Date: 2004-09-01
#
# Description: Useful path on the PDS
#
#############################################################################################
#
# Modified by: Dominik Douville-Belanger
#
# Date: 2005-01-21
# 
# Changes description: Added some useful paths for the PDS-NCCS on the PDS
#
#############################################################################################
"""

# Useful directories 
ROOT = "/apps/pds"
ETC =  ROOT + "/etc"
LOG = ROOT + "/log"
BIN = ROOT + "/bin"
INFO = ROOT + "/info"
CLIENTHOME = ROOT + "/home"

# Useful directorties for PX
PXROOT = "/apps/px"
PXETC = PXROOT + "/etc"
RXETC = PXETC + "/rx"
TXETC = PXETC + "/tx"
TRXETC = PXETC + "/trx"
PXLOG = PXROOT + "/log"
RXQ = PXROOT + "/rxq"
TXQ = PXROOT + "/txq"

# Useful files
PROD = "pdschkprod.conf"
SWITCH = "pdsswitch.conf"
STARTUP = "PDSstartupinfo"
TOGGLE = "ToggleSender"
RESEND = "pdsresend"

# Useful path (directory + file)
FULLPROD = ETC + "/" + PROD
FULLSWITCH = ETC + "/" + SWITCH
FULLSTARTUP = INFO + "/" + STARTUP
FULLTOGGLE = BIN + "/" + TOGGLE

PYTHON2 = "/usr/bin/env python2"
