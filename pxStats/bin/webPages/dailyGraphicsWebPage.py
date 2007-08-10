#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.


##############################################################################
##
##
## Name   : dailyGraphicsWebPage.py 
##
##
## Author : Nicholas Lemay
##
## Date   : 22-11-2006 
##
##
## Description : Generates a web pages that gives access to user 
##               to the daily graphics of the last 7 days for all rx sources 
##               and tx clients.
##
##
##############################################################################
"""


"""
    Small function that adds pxlib to the environment path.  
"""
import os, time, sys
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
import os, time, sys

from PXManager import *
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods


# Constants
LOCAL_MACHINE = os.uname()[1]          
NB_DAYS_DISPLAYED = 7 
    

def getDays():
    """
        Returns the last 3 year numbers including the current year.
    
    """
    
    days = []
    
    startTime = ( time.time() - (NB_DAYS_DISPLAYED*24*60*60) )
    for i in range( 1, NB_DAYS_DISPLAYED + 1 ):
        days.append( ( startTime + ( i*24*60*60 ) ) )   
       
    return days
    
    
    
def getStartEndOfWebPage():
    """
        Returns the time of the first 
        graphics to be shown on the web 
        page and the time of the last 
        graphic to be displayed. 
        
    """
    
    currentTime = StatsDateLib.getIsoFromEpoch( time.time() )  
    
    start = StatsDateLib.rewindXDays( currentTime, NB_DAYS_DISPLAYED - 1 )
    start = StatsDateLib.getIsoTodaysMidnight( start )
         
    end   = StatsDateLib.getIsoTodaysMidnight( currentTime )
        
    return start, end 
    
        

    
def generateWebPage( rxNames, txNames, days ):
    """
        Generates a web page based on all the 
        rxnames and tx names that have run during
        the pas x days. 
        
        Only links to available graphics will be 
        displayed.
        
    """       
        
    rxNamesArray = rxNames.keys()
    txNamesArray = txNames.keys()
    
    rxNamesArray.sort()
    txNamesArray.sort()
            
    #Redirect output towards html page to generate.    
    if not os.path.isdir(StatsPaths.STATSWEBPAGESHTML ):
        os.makedirs( StatsPaths.STATSWEBPAGESHTML )
    
    fileHandle = open( StatsPaths.STATSWEBPAGESHTML  +"dailyGraphs.html" , 'w' )

     
    fileHandle.write( """
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
        <link rel="stylesheet" href="../scripts/js/windowfiles/dhtmlwindow.css" type="text/css" />
        
        <script type="text/javascript" src="../scripts/js/windowfiles/dhtmlwindow.js">
            
            This is left here to give credit to the original 
            creators of the dhtml script used for the group pop ups: 
            /***********************************************
            * DHTML Window Widget-  Dynamic Drive (www.dynamicdrive.com)
            * This notice must stay intact for legal use.
            * Visit http://www.dynamicdrive.com/ for full source code
            ***********************************************/
        
        </script>
        <script type="text/javascript">

            var descriptionWindow=dhtmlwindow.open("description", "inline", "description", "Group description", "width=900px,height=120px,left=150px,top=10px,resize=1,scrolling=0", "recal")
            descriptionWindow.hide()

        </script>
        
        
        <head>
            <title> PX Graphics </title>
        </head>
        <script>
            counter =0;             
            function wopen(url, name, w, h){
            // This function was taken on www.boutell.com
                
                w += 32;
                h += 96;
                counter +=1; 
                var win = window.open(url,
                counter,
                'width=' + w + ', height=' + h + ', ' +
                'location=no, menubar=no, ' +
                'status=no, toolbar=no, scrollbars=no, resizable=no');
                win.resizeTo(w, h);
                win.focus();
            }         
        </script>   
        
        <script>
                function showSourceHelpPage(){
                   var sourceHelpPage = dhtmlwindow.open("sourceHelpPage", "iframe", "helpPages/source.html", "Definition of 'source'", "width=875px,height=100px,resize=1,scrolling=1,center=1", "recal")
                   sourceHelpPage.moveTo("middle", "middle"); 
                }
                
                
                function showClientHelpPage(){
                   var clientHelpPage = dhtmlwindow.open("client", "iframe", "helpPages/client.html", "Definition of 'client'", "width=875px,height=150px,resize=1,scrolling=1,center=1", "recal")
                    .moveTo("middle", "middle");
                }
                
        </script>
        
         
        <STYLE>
            <!--
            A{text-decoration:none}
            -->
        </STYLE>
        
        
        <style type="text/css">
            div.tableContainer {
                width: 95%;        /* table width will be 99% of this*/
                height: 275px;     /* must be greater than tbody*/
                overflow: auto;
                margin: 0 auto;
                }
            
            table {
                width: 99%;        /*100% of container produces horiz. scroll in Mozilla*/
                border: none;
                background-color: #f7f7f7;
                table-layout: fixed;
                }
                
            table>tbody    {  /* child selector syntax which IE6 and older do not support*/
                overflow: auto; 
                height: 225px;
                overflow-x: hidden;
                }
                
            thead tr    {
                position:relative; 
                
                }
                
            thead td, thead th {
                text-align: center;
                font-size: 14px; 
                background-color:"#006699";
                color: steelblue;
                font-weight: bold;
                border-top: solid 1px #d8d8d8;
                }    
                
            td    {
                color: #000;
                padding-right: 2px;
                font-size: 12px;
                text-align: left;
                border-bottom: solid 1px #d8d8d8;
                border-left: solid 1px #d8d8d8;
                }
            
            tfoot td    {
                text-align: center;
                font-size: 11px;
                font-weight: bold;
                background-color: papayawhip;
                color: steelblue;
                border-top: solid 2px slategray;
                }
        
            td:last-child {padding-right: 20px;} /*prevent Mozilla scrollbar from hiding cell content*/
        
        </style>
      
        
        <body text="#000000" link="#FFFFFF" vlink="000000" bgcolor="#FFF4E5" >
        
            <h2>Daily graphics for RX sources from MetPx. <font size = "2">*updated hourly</font></h2>
        
            <div class="tableContainer">         
               <table> 
                   <thead>
        
                        <tr>    
                            <td bgcolor="#006699">
                                <div class = "rxTableEntry">
                                    <font color = "white">
                                        <div class="left">Sources</div>
                                        <a target ="popup" href="#" onClick="showSourceHelpPage(); return false;">
                                            <div class="right">?</div>
                                        </a>
                                    </font>
                                </div>
                            </td>
                            
                            <td bgcolor="#006699">
                                <font color = "white">List of available daily graphics.</font>                                
                            </td>
                        </tr>   
                    </thead>
        
        
                    <tbody>
    
    """)
    
    
    
    for rxName in rxNamesArray :
        if rxNames[rxName] == "" :
            fileHandle.write( """<tr> <td bgcolor="#99FF99"> %s</td> """ %(rxName))
            fileHandle.write( """<td bgcolor="#66CCFF"> Days :   """ )
        else:
            fileHandle.write( """<tr> <td bgcolor="#99FF99"><div class="left"> %s</div><div class="right"><a href="#" onClick="descriptionWindow.load('inline', '%s', 'Group description');descriptionWindow.show(); return false">?</a></div></td> """ %(rxName, rxNames[rxName].replace("'","").replace('"','')))
            fileHandle.write( """<td bgcolor="#66CCFF"> Days :   """ )
            
                
        for day in days:
            
            currentYear, currentMonth, currentDay = StatsDateLib.getYearMonthDayInStrfTime( day )
            
            file = file = StatsPaths.STATSGRAPHSARCHIVES + "daily/rx/%s/"%( rxName ) + str(currentYear) + "/" + str(currentMonth) + "/" + str(currentDay) + ".png"
            webLink = "archives/daily/rx/%s/"%( rxName ) + str(currentYear) + "/" + str(currentMonth) + "/" + str(currentDay) + ".png"
            
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="%s" href="%s">%s   </a>"""%( rxName, webLink, time.strftime( "%a", time.gmtime(day) ) ) )
                
                 
        fileHandle.write( """</td></tr>""" )
    
    fileHandle.write( """
    
            </tbody>
        </table>
    </div>
       
    <h2>Daily graphics for TX clients from MetPx. <font size = "2">*updated hourly</font></h2>
    
    <div class="tableContainer">         
        <table> 
            <thead>
                <tr>

                     <td bgcolor="#006699">
                        <div class = "txTableEntry">
                            <font color = "white">
                                <div class="left">Clients</div>
                                <a target ="popup" href="#" onClick="showClientHelpPage(); return false;">
                                    <div class="right">?</div>
                                </a>
                            </font>
                        </div>
                    </td>
                    
                    <td bgcolor="#006699">
                        <div class = "txTableEntry">
                            <font color = "white">List of available daily graphics.</font>
                        </div>    
                    </td>
            
                </tr>  
         </thead>   
     
     
        <tbody> 
    
       
    """   )       
        
    for txName in txNamesArray : 
        if txNames[txName] == "" :
            fileHandle.write( """<tr> <td bgcolor="#99FF99"> %s</td> """ %(txName))
            fileHandle.write( """<td bgcolor="#66CCFF"><div class = "txTableEntry">   Days :   """ )
        else:
            fileHandle.write( """<tr> <td bgcolor="#99FF99"><div class="left"> %s </div><div class="right"><a href="#" onClick="descriptionWindow.load('inline', '%s', 'Group description');descriptionWindow.show(); return false">?</a></div></td> """ %(txName, txNames[txName].replace("'","").replace('"','') ))
            fileHandle.write( """<td bgcolor="#66CCFF">  Days :   """ )
        
        
        for day in days:
                        
            currentYear, currentMonth, currentDay = StatsDateLib.getYearMonthDayInStrfTime( day )
            file = StatsPaths.STATSGRAPHSARCHIVES + "/daily/tx/%s/"%( txName ) + str(currentYear) + "/" + str(currentMonth) + "/" + str(currentDay) + ".png"
            webLink =  "archives/daily/tx/%s/"%( txName ) + str(currentYear) + "/" + str(currentMonth) + "/" + str(currentDay) + ".png"
            
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="%s" href="%s">%s   </a>"""%( rxName, webLink, time.strftime( "%a", time.gmtime(day) ) ) )     

        fileHandle.write( "</td></tr>" )

    fileHandle.write(  """
      
          </tbody>
    
      </table>    
       
    </body>

</html>
    
    
    
    """ )       
                
    fileHandle.close()                 
        
        
    
def main():   
    
    days = getDays() 
    
    start, end = getStartEndOfWebPage()     
    
    rxNames, txNames = GeneralStatsLibraryMethods.getRxTxNamesForWebPages(start, end)
             
    generateWebPage( rxNames, txNames, days)
    
  
if __name__ == "__main__":
    main()