# -*- coding: UTF-8 -*-
"""Définition d'une sous-classe pour les bulletins "WMO" """

import time
import struct
import string
import curses
import curses.ascii
import bulletin

__version__ = '2.0'

class bulletinWmo(bulletin.bulletin):
        __doc__ = bulletin.bulletin.__doc__ + \
	"""### Ajout de bulletinWmo ###

        Implantation pour un usage concret de la classe bulletin.

	Pour l'instant, un bulletinWmo ne se différencie que par son
	traîtement spécifique.

        Auteur: Louis-Philippe Thériault
        Date:   Octobre 2004
	"""

	def __init__(self,stringBulletin,logger,lineSeparator='\n'):
		bulletin.bulletin.__init__(self,stringBulletin,logger,lineSeparator)

        def doSpecificProcessing(self):
                """doSpecificProcessing()

                   Modifie les bulletins provenant de Washington, transmis 
		   par protocole Wmo, nommés "WMO"

		   Auteur: Louis-Philippe Thériault
		   Date:   Octobre 2004
		"""
                bulletin = self.lineSeparator.join(self.bulletin)

	        if self.getDataType() == 'BI':
	        # Si le bulletin est un BUFR, l'on remplace le premier set,
	        # puis le dernier (apres le 7777) s'il y a lieu
	                bulletin = bulletin.replace('\r\r\n','\n',1)
	                bulletin = bulletin[:bulletin.rfind('7777')] + bulletin[bulletin.rfind('7777'):].replace('\r\r\n','\n')

			self.bulletin = bulletin.splitlines()
	                return 

	        if bulletin[:4] in ['SDUS','WSUS','SRCN','SRMN','SRND','SRWA','SRMT','SXAA','SXCN','SXVX','SXWA','SXXX','FOCN','WAUS']:
        	        bulletin = bulletin.replace('\n\x1e','\n')

	        if bulletin[:4] in ['SRCN','SRMN','SRND','SRWA','SRMT','SXCN','SRUS','SXVX','SXWA']:
        	        bulletin = bulletin.replace('~','\n')

		if bulletin[:2] in ['UK']:
			bulletin = bulletin.replace('\x01','')

                if bulletin[:2] in ['FT']:
                        bulletin = bulletin.replace('\x03','')

                if bulletin[:2] in ['SX','SR']:
                        bulletin = bulletin.replace('\x00','')

                if bulletin[:2] in ['SX']:
                        bulletin = bulletin.replace('\x11','')

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

		# Ramène à un \n à la fin du bulletin
	        bulletin = bulletin.rstrip('\n') + '\n'

	        self.bulletin = bulletin.splitlines()

		# Enlève les espaces à la fin des lignes
		for i in range(len(self.bulletin)):
			self.bulletin[i] = self.bulletin[i].rstrip()
