# -*- coding: UTF-8 -*-
"""Gestion des bulletins "WMO" """

import bulletinManager, bulletinWmo, os, string

__version__ = '2.0'

class bulletinManagerWmo(bulletinManager.bulletinManager):
    __doc__ = bulletinManager.bulletinManager.__doc__ + \
    """### Ajout de bulletinManagerWmo ###

       Spécialisation et implantation du bulletinManager.

       Pour l'instant, un bulletinManagerWmo est pratiquement
       la même chose que le bulletinManager.

       Auteur:      Louis-Philippe Thériault
       Date:        Octobre 2004
    """

    def __init__(self,pathTemp,logger,pathSource=None, \
                    pathDest=None,maxCompteur=99999,lineSeparator='\n',extension=':', \
                    pathFichierCircuit=None,mapEnteteDelai=None,use_pds=0, source=None):

        bulletinManager.bulletinManager.__init__(self,pathTemp,logger, \
                                        pathSource,pathDest,maxCompteur,lineSeparator,extension,pathFichierCircuit,mapEnteteDelai,use_pds, source)

    def _bulletinManager__generateBulletin(self,rawBulletin):
        __doc__ = bulletinManager.bulletinManager._bulletinManager__generateBulletin.__doc__ + \
        """### Ajout de bulletinManagerWmo ###

           Overriding ici pour passer les bons arguments au bulletinWmo

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """
        return bulletinWmo.bulletinWmo(rawBulletin,self.logger,self.lineSeparator)

    def getFileName(self,bulletin,error=False,compteur=True):
        __doc__ = bulletinManager.bulletinManager.getFileName.__doc__ + \
        """### Ajout de bulletinManagerAm ###

           Ajout de la station dans le nom si elle est disponible

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """

        station = None

        if (bulletin.getHeader().split(' ')[0])[:6] == "SRCN40" :
            station = bulletin.getStation()

        if station == None or error:
            return bulletinManager.bulletinManager.getFileName(self,bulletin,error,compteur)
        else:
            nom = bulletinManager.bulletinManager.getFileName(self,bulletin,error,True)

            if compteur:
                nom = ':'.join( [ '_'.join( \
                                        nom.split(':')[0].split('_')[:-1] + [station] + \
                                        nom.split(':')[0].split('_')[-1:]) ] \
                                        + nom.split(':')[1:] )
            else:
            # Pas de compteur
                nom = ':'.join( [ '_'.join( \
                                        nom.split(':')[0].split('_') + [station] ) ] \
                                        + nom.split(':')[1:] )


            return nom
