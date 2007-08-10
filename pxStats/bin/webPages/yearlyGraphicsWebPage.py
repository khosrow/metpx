#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.

##############################################################################
##
##
## Name   : generateGraphics.py 
##
##
## Author : Nicholas Lemay
##
## Date   : 22-11-2006 
##
##
## Description : Generates a web pages that gives access to user 
##               to the yearly graphics of the last 3 years for all rx sources 
##               and tx clients.
##
##
##############################################################################
"""


import os, time, sys
sys.path.insert(1, sys.path[0] + '/../../../')
"""
    Small function that adds pxlib to the environment path.  
"""
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
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods

LOCAL_MACHINE = os.uname()[1]
    
NB_YEARS_DISPLAYED = 3
    
def getYears():
    """
        Returns the last x year numbers including the current year.    
    """
    
    years = []
    
    startTime = (time.time() - ( NB_YEARS_DISPLAYED*365*24*60*60))
    for i in range( 1, NB_YEARS_DISPLAYED + 1 ):
        years.append( startTime + (i*365*24*60*60)  )
   
       
    return years
    
    
    
def getStartEndOfWebPage():
    """
        Returns the time of the first 
        graphics to be shown on the web 
        page and the time of the last 
        graphic to be displayed. 
        
    """
    
    currentTime = StatsDateLib.getIsoFromEpoch( time.time() )  
    
    start = StatsDateLib.rewindXDays( currentTime, ( NB_YEARS_DISPLAYED - 1 ) * 365 )
    start = StatsDateLib.getIsoTodaysMidnight( start )
         
    end   = StatsDateLib.getIsoTodaysMidnight( currentTime )
        
    
    return start, end 
    
        
    
    
def generateWebPage( rxNames, txNames, years ):
    """
        Generates a web page based on all the 
        rxnames and tx names that have run during
        the past x years. 
        
        Only links to available graphics will be 
        displayed.
        
    """   
    
    rxNamesArray = rxNames.keys()
    txNamesArray = txNames.keys()
    
    rxNamesArray.sort()
    txNamesArray.sort()
    
    #Redirect output towards html page to generate.    
    if not os.path.isdir( StatsPaths.STATSWEBPAGESHTML ):
        os.makedirs( StatsPaths.STATSWEBPAGESHTML )     
    fileHandle = open( "%syearlyGraphs.html" %StatsPaths.STATSWEBPAGESHTML , 'w' )

    fileHandle.write(  """
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
                
                function showBytecountHelpPage(){
                   var byteCountHelpPage = dhtmlwindow.open("byteCount", "iframe", "helpPages/byteCount.html", "Definition of 'byteCount'", "width=875px,height=150px,resize=1,scrolling=1,center=1", "recal")
                    byteCountHelpPage.moveTo("middle", "middle");
                }
                
                function showClientHelpPage(){
                   var clientHelpPage = dhtmlwindow.open("client", "iframe", "helpPages/client.html", "Definition of 'client'", "width=875px,height=150px,resize=1,scrolling=1,center=1", "recal")
                    .moveTo("middle", "middle");
                }
                
                function showErrorsHelpPage(){
                   var errorsHelpPage = dhtmlwindow.open("errors", "iframe", "helpPages/errors.html", "Definition of 'errors'", "width=875px,height=150px,resize=1,scrolling=1,center=1", "recal")
                    errorsHelpPage.moveTo("middle", "middle");
                }
                
                function showFilecountHelpPage(){
                   var fileCountHelpPage = dhtmlwindow.open("fileCount", "iframe", "helpPages/fileCount.html", "Definition of 'filecount'", "width=875px,height=150px,resize=1,scrolling=1,center=1", "recal")
                    fileCountHelpPage.moveTo("middle", "middle");
                }
                          
                function showFilesOverMaxLatencyHelpPage(){
                   var filesOverMaxLatencyHelpPage = dhtmlwindow.open("filesOverMaxLatency", "iframe", "helpPages/filesOverMaxLatency.html", "Definition of 'filesOverMaxLatency'", "width=875px,height=150px,resize=1,scrolling=1,center=1", "recal")
                    filesOverMaxLatencyHelpPage.moveTo("middle", "middle");
                }
                
                function showLatencyHelpPage(){
                   var latencyHelpPage = dhtmlwindow.open("byteCount", "iframe", "helpPages/latency.html", "Definition of 'latency'", "width=875px,height=150px,resize=1,scrolling=1,center=1", "recal")
                    latencyHelpPages.moveTo("middle", "middle");
                }
                               
                
            </script>
            
            <script>
                function showSourceHelpPage(){
                   var sourceHelpPage = dhtmlwindow.open("sourceHelpPage", "iframe", "helpPages/source.html", "Definition of 'source'", "width=875px,height=100px,resize=1,scrolling=1,center=1", "recal")
                   sourceHelpPage.moveTo("middle", "middle"); 
                }
                
                function showBytecountHelpPage(){
                   var byteCountHelpPage = dhtmlwindow.open("byteCount", "iframe", "helpPages/byteCount.html", "Definition of 'byteCount'", "width=875px,height=150px,resize=1,scrolling=1,center=1", "recal")
                    byteCountHelpPage.moveTo("middle", "middle");
                }
                
                function showClientHelpPage(){
                   var clientHelpPage = dhtmlwindow.open("client", "iframe", "helpPages/client.html", "Definition of 'client'", "width=875px,height=150px,resize=1,scrolling=1,center=1", "recal")
                    .moveTo("middle", "middle");
                }
                
                function showErrorsHelpPage(){
                   var errorsHelpPage = dhtmlwindow.open("errors", "iframe", "helpPages/errors.html", "Definition of 'errors'", "width=875px,height=150px,resize=1,scrolling=1,center=1", "recal")
                    errorsHelpPage.moveTo("middle", "middle");
                }
                
                function showFilecountHelpPage(){
                   var fileCountHelpPage = dhtmlwindow.open("fileCount", "iframe", "helpPages/fileCount.html", "Definition of 'filecount'", "width=875px,height=150px,resize=1,scrolling=1,center=1", "recal")
                    fileCountHelpPage.moveTo("middle", "middle");
                }
                          
                function showFilesOverMaxLatencyHelpPage(){
                   var filesOverMaxLatencyHelpPage = dhtmlwindow.open("filesOverMaxLatency", "iframe", "helpPages/filesOverMaxLatency.html", "Definition of 'filesOverMaxLatency'", "width=875px,height=150px,resize=1,scrolling=1,center=1", "recal")
                    filesOverMaxLatencyHelpPage.moveTo("middle", "middle");
                }
                
                function showLatencyHelpPage(){
                   var latencyHelpPage = dhtmlwindow.open("byteCount", "iframe", "helpPages/latency.html", "Definition of 'latency'", "width=875px,height=150px,resize=1,scrolling=1,center=1", "recal")
                    latencyHelpPage.moveTo("middle", "middle");
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
            
        </head>    
        
        <body text="#000000" link="#FFFFFF" vlink="000000" bgcolor="#FFF4E5" >

            <h2>Yearly graphics for RX sources from MetPx. <font size = "2">*updated monthly</font></h2>
            <div class="tableContainer">            
            <table> 
               <thead>        
                   <tr>
                            <td bgcolor="#006699">
                                    <font color = "white">
                                        <div class="left">Sources</div>
                                        <a target ="popup" href="#" onClick="showSourceHelpPage(); return false;">
                                            <div class="right">?</div>
                                        </a>
                                    </font>
                            </td>
                            
                            <td bgcolor="#006699" title = "Display the total of bytes received every day of the year for each sources.">
                                    <font color = "white">
                                        <div class="left">Bytecount</div>
                                        <a target ="popup" href="#" onClick="showBytecountHelpPage(); return false;">
                                            <div class="right">?</div>
                                        </a>
                                    </font>
                            </td>
                            
                            <td bgcolor="#006699" title = "Display the total of files received every day of the year for each sources.">
                                    <font color = "white">
                                        <div class="left">Filecount</div>
                                        <a target ="popup" href="#" onClick="showFilecountHelpPage(); return false;">
                                            <div class="right">?</div>
                                        </a>
                                    </font>
                            </td>
                            
                            <td bgcolor="#006699" title = "Display the total of errors that occured during the receptions for every day of the year for each sources.">
                                    <font color = "white">
                                        <div class="left">Errors</div>
                                        <a target ="popup"  href="#" onClick="showErrorsHelpPage(); return false;">
                                            <div class="right">?</div>
                                        </a>
                                    </font>
                            </td>
                        </tr>   
                    </thead>
                    <tbody>           
    
    """ )   
    
    
    for rxName in rxNamesArray :
        if rxNames[rxName] == "" :
            fileHandle.write( """<tr> <td bgcolor="#99FF99"> %s </td> """ %(rxName))
            fileHandle.write( """<td bgcolor="#66CCFF">Years&nbsp;:&nbsp;""" )
        else:
            fileHandle.write( """<tr> <td bgcolor="#99FF99"><div class="left"> %s </div><div class="right"><a href="#" onClick="descriptionWindow.load('inline', '%s', 'Group description');descriptionWindow.show(); return false">?</a></div></td> """ %(rxName, rxNames[rxName].replace("'","").replace('"','')))
            fileHandle.write( """<td bgcolor="#66CCFF">Years&nbsp;:&nbsp;""" )
                   
        for year in years:
            currentYear, currentMonth, currentDay = StatsDateLib.getYearMonthDayInStrfTime( year )   
            
            file = StatsPaths.STATSGRAPHSARCHIVES + "yearly/rx/%s/"%( rxName ) + "bytecount/%s.png" %str(currentYear)         
            webLink = "archives/yearly/rx/%s/"%( rxName ) + "bytecount/%s.png" %str(currentYear)
            
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( rxName, webLink , time.strftime("%Y",time.gmtime(year) ) ) ) 
        
        fileHandle.write( "</td>" )      
    
        fileHandle.write(  """ <td bgcolor="#66CCFF">Years&nbsp;:&nbsp;""" )
        
        
        
        for year in years:
            
            currentYear, currentMonth, currentDay = StatsDateLib.getYearMonthDayInStrfTime( year )            
            file = StatsPaths.STATSGRAPHSARCHIVES + "yearly/rx/%s/"%( rxName ) + "filecount/%s.png" %str(currentYear)
            webLink = "archives/yearly/rx/%s/"%( rxName ) + "filecount/%s.png" %str(currentYear)
            
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( rxName, webLink , time.strftime("%Y",time.gmtime(year) ) ) ) 
        
        fileHandle.write( "</td>" )    
        
        
        fileHandle.write(  """ <td bgcolor="#66CCFF">Years&nbsp;:&nbsp;""" )
        
        for year in years:
            currentYear, currentMonth, currentDay = StatsDateLib.getYearMonthDayInStrfTime( year )            
            file    = StatsPaths.STATSGRAPHSARCHIVES + "yearly/rx/%s/"%( rxName ) + "errors/%s.png" %str(currentYear)
            webLink = "archives/yearly/rx/%s/"%( rxName ) + "errors/%s.png" %str(currentYear)
            
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( rxName, file , time.strftime("%Y",time.gmtime(year) ) ) ) 
        
        fileHandle.write( "</td></tr>" )    
              
    
    fileHandle.write(  """
                    </tbody>
            </table>
        </div>    
    
    <h2>Yearly graphics for TX clients from MetPx. <font size = "2">*updated monthly</font></h2>
        
        <div class="tableContainer">         
            <table> 
               <thead>
                    <tr>

            
                        <td bgcolor="#006699">
                                <font color = "white">
                                    <div class="left">Clients</div>
                                    <a target ="popup" href="#" onClick="showClientHelpPage(); return false;">
                                        <div class="right">?</div>
                                    </a>
                                </font>
                        </td>
                        
                        <td bgcolor="#006699" title = "Display the average latency of file transfers for every day of the year for each clients.">
                                <font color = "white">
                                    <div class="left">Latency</div>
                                     <a target ="popup" href="#" onClick="showLatencyHelpPage(); return false;">
                                        <div class="right">?</div>
                                     </a>
                                </font>
                        </td>
                        
                        <td bgcolor="#006699" title = "Display the total number of files for wich the latency was over 15 seconds for every day of the year for each clients.">
                                <font color = "white">
                                    <div class="left">Files Over Max. Lat.</div>
                                    <a target ="popup" href="#" onClick="showFilesOverMaxLatencyHelpPage(); return false;">
                                        <div class="right">?</div>
                                    </a>
                                </font>
                        </td>
                        
                        <td bgcolor="#006699" title = "Display the total of bytes transfered every day of the year for each clients.">
                                <font color = "white">
                                    <div class="left">Bytecount</div>
                                    <a target ="popup" href="#" onClick="showBytecountHelpPage(); return false;">
                                        <div class="right">?</div>
                                    </a>
                                </font>
                        </td>
                        
                        <td bgcolor="#006699" title = "Display the total of files transferred every day of the year for each clients.">
                                <font color = "white">
                                    <div class="left">Filecount</div>
                                    <a target ="popup" href="#" onClick="showFilecountHelpPage(); return false;">
                                        <div class="right">?</div>
                                    </a>
                                </font>
                        </td>
                        
                        <td bgcolor="#006699" title = "Display the total of errors that occured during file transfers every day of the year for each clients.">
                                <font color = "white">
                                    <div class="left">Errors</div>
                                    <a target ="popup" href="#" onClick="showErrorsHelpPage(); return false;">
                                        <div class="right">?</div>
                                    </a>
                                </font>
                        </td>
            
                    </tr>  
                </thead>
            <tbody>
         
    
    """)          
        
    for txName in txNamesArray : 
        if txNames[txName] == "" :
            fileHandle.write( """ <tr> <td bgcolor="#99FF99">%s</td> """ %(txName))
            fileHandle.write( """<td bgcolor="#66CCFF">Years&nbsp;:&nbsp;""" )
        else:
            fileHandle.write( """<tr> <td bgcolor="#99FF99"><div class="left"> %s </div><div class="right"><a href="#" onClick="descriptionWindow.load('inline', '%s', 'Group description');descriptionWindow.show(); return false">?</a></div></td> """ %(txName, txNames[txName].replace("'","").replace('"','') ))
            fileHandle.write( """<td bgcolor="#66CCFF">Years&nbsp;:&nbsp;""" )
            
       
        for year in years:
            currentYear, currentMonth, currentDay = StatsDateLib.getYearMonthDayInStrfTime( year )            
            file = StatsPaths.STATSGRAPHSARCHIVES + "yearly/tx/%s/"%( txName ) + "latency/%s.png" %str(currentYear)
            webLink = "archives/yearly/tx/%s/"%( txName ) + "latency/%s.png" %str(currentYear)
            
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( txName, webLink , time.strftime("%y",time.gmtime(year) ) ) )
        
        fileHandle.write( "</td>" )
        
        fileHandle.write(  """ <td bgcolor="#66CCFF">Years&nbsp;:&nbsp;""" )
        
        for year in years:
            
            currentYear, currentMonth, currentDay = StatsDateLib.getYearMonthDayInStrfTime( year )            
            
            file = StatsPaths.STATSGRAPHSARCHIVES + "yearly/tx/%s/"%( txName ) + "filesOverMaxLatency/%s.png" %str(currentYear)
            webLink =  "archives/yearly/tx/%s/"%( txName ) + "filesOverMaxLatency/%s.png" %str(currentYear)
            
            
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( txName, webLink , time.strftime("%y",time.gmtime(year) ) ) )
        
        fileHandle.write( "</td>" )
        
        fileHandle.write(  """ <td bgcolor="#66CCFF">Years&nbsp;:&nbsp;""" )
        
        for year in years:
            
            currentYear, currentMonth, currentDay = StatsDateLib.getYearMonthDayInStrfTime( year )            
            file = StatsPaths.STATSGRAPHSARCHIVES + "yearly/tx/%s/"%( txName ) + "bytecount/%s.png" %str(currentYear)
            webLink = "archives/yearly/tx/%s/"%( txName ) + "bytecount/%s.png" %str(currentYear)
            
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( txName, webLink , time.strftime("%y",time.gmtime(year) ) ) )
        
        fileHandle.write( "</td>" )
        
        fileHandle.write(  """ <td bgcolor="#66CCFF">Years&nbsp;:&nbsp;""" )
        
        for year in years:
            
            currentYear, currentMonth, currentDay = StatsDateLib.getYearMonthDayInStrfTime( year )            
            file = StatsPaths.STATSGRAPHSARCHIVES + "yearly/tx/%s/"%( txName ) + "filecount/%s.png" %str(currentYear)
            webLink = "archives/yearly/tx/%s/"%( txName ) + "filecount/%s.png" %str(currentYear)
            
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( txName, webLink , time.strftime("%y",time.gmtime(year) ) ) )
        
        fileHandle.write( "</td>" )
        
        fileHandle.write(  """ <td bgcolor="#66CCFF">Years&nbsp;:&nbsp;""" )
        
        for year in years:
            
            currentYear, currentMonth, currentDay = StatsDateLib.getYearMonthDayInStrfTime( year )            
            
            file    = StatsPaths.STATSGRAPHSARCHIVES + "yearly/tx/%s/"%( txName ) + "errors/%s.png" %str(currentYear)
            webLink = "archives/yearly/tx/%s/"%( txName ) + "errors/%s.png" %str(currentYear) 
            
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( txName, webLink , time.strftime("%y",time.gmtime(year) ) ) )
        
        fileHandle.write( "</td></tr>" )

        

    fileHandle.write(  """       
                    </tbody>
                </table>
           </div>
        </body>
    </html>
    
    
    
    """ )     
                
    fileHandle.close()                 
    

        
def main():        
    
    years = getYears() 
    
    start, end = getStartEndOfWebPage()     
    
    rxNames, txNames = GeneralStatsLibraryMethods.getRxTxNamesForWebPages(start, end)
             
    generateWebPage( rxNames, txNames, years )
    
    
if __name__ == "__main__":
    main()