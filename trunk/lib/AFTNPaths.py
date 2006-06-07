"""
#############################################################################################
# Name: AFTNPaths.py
#
# Author: Daniel Lemay
#
# Date: 2006-03-27
#
# Description: Useful AFTN Paths
#
#############################################################################################
"""
import os, os.path

def normalPaths():

    global ROOT, BIN, LIB, LOG, ETC, RXQ, TXQ, DB, RX_CONF, TX_CONF, TO_SEND, RECEIVED, SENT, \
           TO_SEND_PRO, RECEIVED_PRO, SENT_PRO, SPECIAL_ORDERS, SPECIAL_ORDERS_PRO, STATE

    try:
        envVar = os.path.normpath(os.environ['AFTNROOT'])
    except KeyError:
        envVar = '/apps/px/aftn'

    ROOT = envVar + '/'
    BIN = ROOT + 'bin/'
    LIB = ROOT + 'lib/'
    LOG = ROOT + 'log/'
    ETC = ROOT + 'etc/'
    RXQ = ROOT + 'rxq/'
    TXQ = ROOT + 'txq/'
    DB = ROOT + 'db/'
    RX_CONF = ETC + 'rx/'
    TX_CONF = ETC + 'tx/'

    TO_SEND = ROOT + 'toSendAFTN'
    RECEIVED = ROOT + 'receivedAFTN'
    SENT = ROOT + 'sentAFTN'
    SPECIAL_ORDERS = ROOT + 'specialOrders'

    TO_SEND_PRO = ROOT + 'toSendAFTN_pro'
    RECEIVED_PRO = ROOT + 'receivedAFTN_pro'
    SENT_PRO = ROOT + 'sentAFTN_pro'
    SPECIAL_ORDERS_PRO = ROOT + 'specialOrders_pro'

    STATE = ROOT + 'state/state.obj'

def drbdPaths(rootPath):

    global ROOT, BIN, LIB, LOG, ETC, RXQ, TXQ, DB, RX_CONF, TX_CONF

    ROOT = os.path.normpath(rootPath) + '/'
    BIN = ROOT + 'bin/'
    LIB = ROOT + 'lib/'
    LOG = '/apps/px/' + 'log/'
    ETC = ROOT + 'etc/'
    RXQ = ROOT + 'rxq/'
    TXQ = ROOT + 'txq/'
    DB = ROOT + 'db/'
    RX_CONF = ETC + 'rx/'
    TX_CONF = ETC + 'tx/'
