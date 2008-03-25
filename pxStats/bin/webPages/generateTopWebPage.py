#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.

##############################################################################
##
##
## Name   : generateTopWebPage.py 
##
##
## @author: Nicholas Lemay
##
## @since: 12-04-2007, last update on 2007-07-17 
##
##
## Description : Generates the top frame to be displayed on the pxstats web 
##               site.
##
##############################################################################
"""

"""
    Small function that adds pxlib to the environment path.  
"""

import gettext, os, time, sys, datetime, string
sys.path.insert(1, sys.path[0] + '/../../../')
try:
    pxlib = os.path.normpath( os.environ['PXROOT'] ) + '/lib/'
except KeyError:
    pxlib = '/apps/px/lib/'
sys.path.append(pxlib)


"""
    Imports
    PXManager requires pxlib 
"""
from PXManager import *
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsConfigParameters import StatsConfigParameters
from pxStats.lib.MachineConfigParameters import MachineConfigParameters
   
LOCAL_MACHINE = os.uname()[1]   


def generateWebPage( machineTags, language = 'en' ):
    """
        @summary :  Generates the top.html web page
                    to be displayed as the top frame
                    of the pxstats web site.
        
        @param machineTags  : Tags representing machine groups 
                              for which we are producing graphics.              
        
        @param language : Language for which to generate the web page.
                    
    """
    
    if language == 'fr':
        fileName = StatsPaths.STATSLANGFRBINWEBPAGES + "generateTopWebPage" 
    elif language == 'en':
        fileName = StatsPaths.STATSLANGENBINWEBPAGES + "generateTopWebPage" 
    
    
    
    translator = gettext.GNUTranslations(open(fileName))
    _ = translator.gettext

    file = "%stop_%s.html" %( StatsPaths.STATSWEBPAGES, language )
    fileHandle = open( file , 'w' )

    fileHandle.write( """

    <html>

    <style type="text/css">
        div.left { float: left; }
        div.right {float: right; }
    </style>

    <body text="white" link="white" vlink="white" bgcolor="#006699" >

        <div class="left">
            """ + _("Individual graphics") + """&nbsp;&nbsp;:&nbsp;&nbsp;

             <a href="html/dailyGraphs_%s.html target="bottom">"""%language  + _("Daily") + """</a>
            &nbsp;&nbsp;

             <a href="html/weeklyGraphs_%s.html target="bottom">"""%language + _("Weekly")  + """</a>
            &nbsp;&nbsp;

             <a href="html/monthlyGraphs_%s.html target="bottom">"""%language + _("Monthly") + """</a>
            &nbsp;&nbsp;

             <a href="html/yearlyGraphs_%s.html" target="bottom">""" %language +_("Yearly") + """</a>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;

    """   )


    if machineTags != [] :
        fileHandle.write( """
        """ + _("Clusters") + """&nbsp;&nbsp;:&nbsp;&nbsp;&nbsp;
        """ )

        for machineTag in machineTags:
            fileHandle.write( """
            <a href="html/%s_%s.html" target="bottom">%s</a>
            &nbsp;&nbsp;&nbsp;
             """ %( machineTag.replace( ',','' ),language , string.upper(machineTag) ) )


    fileHandle.write( """
        </div>

        <div class="right">
            <a href="archives" target="bottom" >Archives</a>

             <a href="../scripts/cgi-bin/graphicsRequestPage.py?lang=%s" target="bottom">"""%language + _("Requests") + """</a>

             <a href="html/helpPages/glossary_%s.html" target="bottom" >""" %language + _("Glossary") + """</a>
        </div>



    </body>

</html>


    """ )


    fileHandle.close()



def main():
    """
    """
    
    configParameters = StatsConfigParameters()
    configParameters.getAllParameters()
    machineParameters = MachineConfigParameters()
    machineParameters.getParametersFromMachineConfigurationFile()    
    generateWebPage(  configParameters.sourceMachinesTags )
    machineNames     = machineParameters.getPairedMachinesAssociatedWithListOfTags( configParameters.sourceMachinesTags )

    
    
     
    
if __name__ == "__main__":
    main()    
