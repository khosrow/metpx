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
	        if self.getDataType() == 'BI':
	        # Si le bulletin est un BUFR, l'on remplace le premier set,
	        # puis le dernier (apres le 7777) s'il y a lieu
	                self.replaceChar('\r\r\n',self.lineSeparator)
	                return 

	        if self.bulletin[0][:4] in ['SDUS','WSUS','SRCN','SRMN','SRND','SRWA','SRMT','SXAA','SXCN','SXVX','SXWA','SXXX','FOCN','WAUS']:
        	        self.replaceChar('\n\x1e',self.lineSeparator)

	        if self.bulletin[0][:4] in ['SRCN','SRMN','SRND','SRWA','SRMT','SXCN','SRUS','SXVX','SXWA']:
        	        self.replaceChar('~',self.lineSeparator)

		if self.bulletin[0][:2] in ['UK']:
			self.replaceChar('\x01','')

                if self.bulletin[0][:2] in ['FT']:
                        self.replaceChar('\x03','')

                if self.bulletin[0][:2] in ['SX','SR']:
                        self.replaceChar('\x00','')

                if self.bulletin[0][:2] in ['SX']:
                        self.replaceChar('\x11','')

	        if self.bulletin[0][:4] in ['SRUS']:
        	        self.replaceChar('\t','')

	        if self.bulletin[0][:4] in ['WWST']:
        	        self.replaceChar('\xba','')

	        if self.bulletin[0][:4] in ['USXX']:
        	        self.replaceChar('\x18','')

	        if self.bulletin[0][:4] in ['SRUS']:
        	        self.replaceChar('\x1a','')

	        if self.bulletin[0][:4] in ['SRMT']:
        	        self.replaceChar('\x12','')

	        if self.bulletin[0][:4] in ['SXUS','SXCN']:
        	        self.replaceChar('\x7f','?')

	        if self.bulletin[0][:4] in ['SXVX','SRUS']:
	                self.replaceChar('\x7f','')

	        self.replaceChar('\r','')

	        if self.bulletin[0][:2] in ['SA','SM']:
	                self.replaceChar('\x03\n','')

		# Re-calcul du bulletin
		self.bulletin = self.splitlinesBulletin(self.lineSeparator.join(self.bulletin))

		# Enlève les espaces à la fin des lignes
		for i in range(len(self.bulletin)):
			self.bulletin[i] = self.bulletin[i].rstrip()
