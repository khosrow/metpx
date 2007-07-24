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
import os, time, sys, datetime, string
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



def generateWebPage( machineTags ):
    """
        Generates the top.html web page
        to be displayed as the top frame
        of the pxstats web site.
    """

    file = "%stop.html" %StatsPaths.STATSWEBPAGES 
    fileHandle = open( file , 'w' )
    
    fileHandle.write( """ 
    <html>
    
    <style type="text/css">
        div.left { float: left; }
        div.right {float: right; }
    </style>
    
    <body text="white" link="white" vlink="white" bgcolor="#006699" >
        
        <div class="left">
            Individual graphics&nbsp;&nbsp;:&nbsp;&nbsp;
            <a href="html/dailyGraphs.html" target="bottom">Daily</a> 
            &nbsp;&nbsp;            
            <a href="html/weeklyGraphs.html" target="bottom">Weekly</a>
            &nbsp;&nbsp;
            <a href="html/monthlyGraphs.html" target="bottom">Monthly</a>
            &nbsp;&nbsp;
            <a href="html/yearlyGraphs.html" target="bottom">Yearly</a>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  
            
       
       
    """)
    
    
    if machineTags != [] :
        fileHandle.write( """
        Combined graphics&nbsp;&nbsp;:&nbsp;&nbsp;&nbsp;
        """ )    
        
        for machineTag in machineTags:
            fileHandle.write( """
            <a href="html/%s.html" target="bottom">%s</a> 
            &nbsp;&nbsp;&nbsp;              
            """ %( machineTag.replace( ',','' ), string.upper(machineTag) ) ) 
    
        
    fileHandle.write( """ 
        </div> 
        
        <div class="right">
            <a href="%s" target="bottom" >Archives</a>
            <a href="../scripts/cgi-bin/graphicsRequestPage.py" target="bottom">Requests</a>
            <a href="html/glossary.html" target="bottom" >Glossary</a>
        </div>
        
        
    
    </body>    

</html>
           
    
    """ %( StatsPaths.STATSGRAPHSARCHIVES ) )
    
    
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