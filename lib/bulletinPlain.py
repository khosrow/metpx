# -*- coding: UTF-8 -*-
"""Définition d'une classe concrète pour les bulletins"""

import bulletin

__version__ = '2.0'

class bulletinPlain(bulletin.bulletin):
	__doc__ = bulletin.bulletin.__doc__ + \
	"""
	### Ajout de bulletinPlain ###

	Implantation minimale d'un bulletin abstrait.

	Concrètement, doSpecificProcessing ne fait rien.

	Auteur:	Louis-Philippe Thériault
	Date:	Novembre 2004
  	"""

	def doSpecificProcessing(self):
		"""doSpecificProcessing()

		   Fait rien

                   Auteur:      Louis-Philippe Thériault
                   Date:        Octobre 2004
		"""
		return
