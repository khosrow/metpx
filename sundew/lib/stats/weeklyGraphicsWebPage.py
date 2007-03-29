#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

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
##               to the weekly graphics of the last 5 weeks for all rx sources 
##               and tx clients.
##
##
##############################################################################


import os, time,sys
import generalStatsLibraryMethods
from generalStatsLibraryMethods import *
from PXPaths   import * 
from PXManager import *

LOCAL_MACHINE = os.uname()[1]      
   
    
def getWeekNumbers():
    """
        Returns the 3 week numbers including current week number.
    
    """
    
    weekNumbers = []
    
    startTime = (time.time() - (3*7*24*60*60))
    for i in range(1,4):
        weekNumbers.append( time.strftime("%W",time.gmtime(startTime + (i*7*24*60*60))) )
   
    return weekNumbers
    
    
def main():        
    

    
    rxNames,txNames = generalStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, "pds5" )
    pxatxrxNames,pxatxtxNames = generalStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, "pxatx" )
    
    rxNames.extend(pxatxrxNames)
    txNames.extend(pxatxtxNames)
    
    rxNames.sort()
    txNames.sort()
    weekNumbers = getWeekNumbers()
    
    
    #Redirect output towards html page to generate.   
    if not os.path.isdir("/apps/px/stats/webPages/"):
        os.makedirs( "/apps/px/stats/webPages/" )      
    fileHandle = open( "/apps/px/stats/webPages/weeklyGraphs.html" , 'w' )


    fileHandle.write(  """
    <html>
        <STYLE>
            <!--
            A{text-decoration:none}
            -->
        </STYLE>
        
        
        <style type="text/css">
            div.left { float: left; }
            div.right {float: right; }
            
        div.txScroll {
            height: 200px;
            width: 1255px;
            overflow: auto;
            word-wrap:break-word;
            border: 0px ;                    
            padding: 0px;
        }
            
        div.txTableEntry{
            width:177px;            
            height: 10px;
        }
        
        div.rxScroll {
            height: 200px;
            width: 1255px;
            overflow: auto;
            word-wrap:break-word;
            border: 0px ;                    
            padding: 0px;
        }
            
        div.rxTableEntry{
            width:277px;            
            height: 10px;
        }
        
        
        </style>
        
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
            
            
        </head>    
        <body text="#000000" link="#FFFFFF" vlink="000000" bgcolor="#CCCCCC" >
        
        <br>
        <h2>Weekly graphics for RX sources from MetPx.  <font size = "2">*updated hourly</font></h2>
                
        <table cellspacing=10 cellpadding=8 id=header bgcolor="#cccccc">
        
            <tr>
                <td bgcolor="#006699">
                    <div class = "rxTableEntry">
                        <font color = "white">
                            <div class="left">
                            Sources                            
                            </div>
                            <a target ="popup" href="%s" onClick="wopen('helpPages/source.html', 'popup', 875, 100); return false;">
                                <div class="right">
                                ?
                                </div>
                            </a>    
                        </font>      
                    </div>
                </td>
                
                <td bgcolor="#006699" title = "Display the total of bytes received every day of the week for each sources.">
                    <div class = "rxTableEntry">
                        <font color = "white">
                            <div class="left">
                            Bytecount
                            </div>
                            <a target ="popup" href="%s" onClick="wopen('helpPages/byteCount.html', 'popup', 875, 100); return false;">
                                <div class="right">
                                ?
                                </div>
                            </a>
                        </font>
                    </div>
                </td>
                
                <td bgcolor="#006699" title = "Display the total of files received every day of the week for each sources.">
                    <div class = "rxTableEntry">
                        <font color = "white">
                            <div class="left">Filecount</div>
                            <a target ="popup" href="%s" onClick="wopen('helpPages/fileCount.html', 'popup', 875, 100); return false;">                            
                                <div class="right">?</div>                            
                            </a>
                        </font>
                    </div>                
                </td>
                
                <td bgcolor="#006699" title = "Display the total of errors that occured during the receptions for every day of the week for each sources.">
                    <div class = "rxTableEntry">
                        <font color = "white">
                            <div class="left">Errors</div>
                            <a target ="popup"  href="%s" onClick="wopen('helpPages/errors.html', 'popup', 875, 100); return false;">
                                <div class="right">?</div>
                            </a>
                        </font>
                    </div>
                
                </td>
            </tr>
        
        </table>
        
        <div class="rxScroll">    
                
    """ )    
    
    
    for rxName in rxNames :
        
        fileHandle.write(  """<table cellspacing=10 cellpadding=8> <tr><td bgcolor="#99FF99"><div class = "rxTableEntry"> %s </div></td>""" %(rxName) )
        
        fileHandle.write(  """ <td bgcolor="#66CCFF"><div class = "rxTableEntry">Weeks&nbsp;:&nbsp;""" )
        
        for week in weekNumbers:
            file = "%swebGraphics/weekly/bytecount/%s/%s.png" % (PXPaths.GRAPHS, rxName, week )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( rxName, file , week ) ) 
        
        fileHandle.write( "</div></td>" )    
    
    
        
        fileHandle.write(  """ <td bgcolor="#66CCFF"><div class = "rxTableEntry">Weeks&nbsp;:&nbsp;""" )
        
        for week in weekNumbers:
            file = "%swebGraphics/weekly/filecount/%s/%s.png" % (PXPaths.GRAPHS, rxName, week )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( rxName, file , week ) ) 
        
        fileHandle.write( "</div></td>" ) 
        
        
        fileHandle.write(  """ <td bgcolor="#66CCFF"><div class = "rxTableEntry">Weeks&nbsp;:&nbsp;""" )
        
        for week in weekNumbers:
            file = "%swebGraphics/weekly/errors/%s/%s.png" % (PXPaths.GRAPHS, rxName, week )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">%s&nbsp;</a>"""%( rxName, file , week ) ) 
        
        fileHandle.write( "</div></td></tr></table>" )                            
    
        
        
    fileHandle.write(  """    
    </div> 
    
    <br>        
    
    <h2>Weekly graphics for TX clients from MetPx.  <font size = "2">*updated hourly</font></h2>    
    
        <table cellspacing=10 cellpadding=8 id=header bgcolor="#cccccc">        
            <tr>

                <td bgcolor="#006699">
                    <div class = "txTableEntry">
                        <font color = "white">
                            <div class="left">Clients</div>
                            <a target ="popup" href="%s" onClick="wopen('helpPages/client.html', 'popup', 875, 100); return false;">
                                <div class="right">?</div>
                            </a>
                        </font> 
                    </div>
                </td>
            
                <td bgcolor="#006699" title = "Display the taverage latency of file transfers for every day of the week for each clients.">
                    <div class = "txTableEntry">
                        <font color = "white"><div class="left">Latency</div>
                            <a target ="popup" href="%s" onClick="wopen('helpPages/latency.html', 'popup', 875, 100); return false;">
                                <div class="right">?</div>
                            </a>
                        </font>
                    </div>
                </td>
            
                <td bgcolor="#006699" title = "Display the total number of files for wich the latency was over 15 seconds for every day of the week for each clients.">
                    <div class = "txTableEntry">
                        <font color = "white"><div class="left">Files Over Max. Lat.</div>
                            <a target ="popup" href="%s" onClick="wopen('helpPages/filesOverMaxLatency.html', 'popup', 875, 100); return false;">
                                <div class="right">?</div>
                            </a>
                        </font>
                    </div>                
                </td>
            
                <td bgcolor="#006699" title = "Display the total of bytes transfered every day of the week for each clients.">
                    <div class = "txTableEntry">
                        <font color = "white">                 
                            <div class="left">Bytecount</div>
                             <a target ="popup" href="%s" onClick="wopen('helpPages/byteCount.html', 'popup', 875, 100); return false;">
                                    <div class="right">?</div>
                             </a>                            
                        </font>
                    </div>
                </td>
                
                <td bgcolor="#006699"  title = "Display the total of files transferred every day of the week for each clients.">
                    <div class = "txTableEntry">
                        <font color = "white">
                            <div class="left">Filecount</div>
                            <a target ="popup" href="%s" onClick="wopen('helpPages/fileCount.html', 'popup', 875, 100); return false;">
                                <div class="right">?</div>
                            </a>
                        </font>
                    </div>                
                </td>
                
                <td bgcolor="#006699" title = "Display the total of errors that occured during file transfers every day of the week for each clients.">
                    <div class = "txTableEntry">
                        <font color = "white">
                            <div class="left">Errors</div>
                            <a target ="popup" href="%s" onClick="wopen('helpPages/errors.html', 'popup', 875, 100); return false;">
                                <div class="right">?</div>
                            </a>
                        </font>
                    </div>                
                </td>
            
            </tr>
        
        </table>
        
        <div class="txScroll">                
        
    """ )
         
    for txName in txNames : 
        fileHandle.write(  """<table cellspacing=10 cellpadding=8> <tr><td bgcolor="#99FF99"><div class = "txTableEntry">%s </div></td>""" %(txName) )
        
        fileHandle.write(  """ <td bgcolor="#66CCFF"><div class = "txTableEntry">Weeks&nbsp;:&nbsp;""" )
        
        for week in weekNumbers:
            file = "%swebGraphics/weekly/latency/%s/%s.png" % (PXPaths.GRAPHS, txName, week )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">&nbsp;%s</a>"""%( txName, file , week ) )
        
        fileHandle.write( "</div></td>" )
        

        fileHandle.write(  """ <td bgcolor="#66CCFF"><div class = "txTableEntry">Weeks&nbsp;:&nbsp;""" )
        
        for week in weekNumbers:
            file = "%swebGraphics/weekly/filesOverMaxLatency/%s/%s.png" % (PXPaths.GRAPHS, txName, week )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">&nbsp;%s</a>"""%( txName, file, week ) )
        
        fileHandle.write( "</div></td>" )  
        
        
        fileHandle.write(  """ <td bgcolor="#66CCFF"><div class = "txTableEntry">Weeks&nbsp;:&nbsp;""" )
        
        for week in weekNumbers:
            file = "%swebGraphics/weekly/bytecount/%s/%s.png" % (PXPaths.GRAPHS, txName, week )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">&nbsp;%s</a>"""%( txName, file, week ) )
        
        fileHandle.write( "</div></td>" )    
        
        fileHandle.write(  """<td bgcolor="#66CCFF"><div class = "txTableEntry">Weeks&nbsp;:&nbsp;""" )
        
        for week in weekNumbers:
            file = "%swebGraphics/weekly/filecount/%s/%s.png" % (PXPaths.GRAPHS, txName, week )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">&nbsp;%s</a>"""%( txName, file, week ) )
        
        fileHandle.write( "</div></td>" )   
        
        fileHandle.write(  """ <td bgcolor="#66CCFF"><div class = "txTableEntry">Weeks&nbsp;:&nbsp;""" )
        
        for week in weekNumbers:
            file = "%swebGraphics/weekly/errors/%s/%s.png" % (PXPaths.GRAPHS, txName, week )
            if os.path.isfile( file ):
                fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">&nbsp;%s</a>"""%( txName, file, week ) )
        
        fileHandle.write( "</div></td></tr></table>" )    
 
        

    fileHandle.write(  """    
    
    </div>
    </body>
    </html>
    
    
    
    """  )      
                
    fileHandle.close()                 
    

if __name__ == "__main__":
    main()