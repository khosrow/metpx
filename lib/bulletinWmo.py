"""Définition d'une sous-classe pour les bulletins "wmo"


"""

import time
import struct
import string
import curses
import curses.ascii
import bulletin

__version__ = '2.0'

class bulletinWmo(bulletin.bulletin):

        def doSpecificProcessing(self):
                """doSpecificProcessing()

                   Modifie les bulletins provenant de Washington, transmis 
		   par protocole Wmo, nommés "WMO" """
		bulletin = self.bulletin

	        if bulletin[:4] in ['SDUS','WSUS','SRCN','SRMN','SRND','SRWA','SRMT','SXAA','SXCN','SXVX','SXWA','SXXX','FOCN','WAUS']:
        	        bulletin = bulletin.replace('\n\x1e','\n')

	        if bulletin[:4] in ['SRCN','SRMN','SRND','SRWA','SRMT','SXCN','SRUS','SXVX','SXWA']:
        	        bulletin = bulletin.replace('~','\n')

	        if bulletin[-1] != '\n':
        	        bulletin = bulletin + '\n'

	        if bulletin[:4] in ['SRUS']:
        	        bulletin = bulletin.replace('\t','')

	        if bulletin[:4] in ['WWST']:
        	        bulletin = bulletin.replace('\xba','')

	        if bulletin[:4] in ['USXX']:
        	        bulletin = bulletin.replace('\x18','')

	        if bulletin[:4] in ['SRUS']:
        	        bulletin = bulletin.replace('\x1a','')

	        if bulletin[:4] in ['SRMT']:
        	        bulletin = bulletin.replace('\x12','')

	        if bulletin[:4] in ['SXUS','SXCN']:
        	        bulletin = bulletin.replace('\x7f','?')

	        if bulletin[:4] in ['SXVX','SRUS']:
	                bulletin = bulletin.replace('\x7f','')

	        bulletin = bulletin.replace('\r','')

	        if bulletin[:2] in ['SA','SM']:
	                bulletin = bulletin.replace('\x03\n','')

	        if bulletin[-2:] == '\n\n':
	                bulletin = bulletin[:-1]

	        self.bulletin = bulletin


