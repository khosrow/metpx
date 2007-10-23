#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
##############################################################################
##
##
## Name   : totalGraphicsWebPages.py 
##
##
## Author : Nicholas Lemay
##
## Date   : 25-01-2007 
##
##
## Description : Generates the web pages that gives access to users
##               to the graphics based on the data totals of all the 
##               rx sources or tx clients combined. Daily, weekly, monthly,
##               and yearly graphics will be made available through these
##               pages.
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
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.StatsConfigParameters import StatsConfigParameters
from pxStats.lib.MachineConfigParameters import MachineConfigParameters

   
LOCAL_MACHINE = os.uname()[1]   


def getDays():
    """
        Returns the last 5 days numbers including the current year.
    
    """
    
    days = []
    
    startTime = (time.time() - (7*24*60*60))
    for i in range(1,8):
        days.append( startTime + ( i*24*60*60 ) )
   
       
    return days
    
    
        
def getWeeks():
    """
        Returns the 5 week numbers including current week number.
    
    """
    
    weeks = []
    
    startTime = (time.time() - (5*7*24*60*60))
    for i in range(1,6):
        weeks.append( startTime + (i*7*24*60*60) )
   
    return weeks
    
    
    
def getMonths():
    """
        Returns the 3 months including current month.
    
    """
    
    currentTime = time.time()
    currentTime = StatsDateLib.getIsoFromEpoch( currentTime )
    currentDate = datetime.date( int(currentTime[0:4]), int(currentTime[5:7]), 1 )     
       
    months = []
    
       
    for i in range(0,5):
        
        if currentDate.month -i < 1 :
            month = currentDate.month -i + 12
            year  = currentDate.year -i 
        else :     
            month = currentDate.month -i 
            year = currentDate.year
            
        if currentDate.day > 28:
            day = currentDate.day -5
        else: 
            day = currentDate.day          
        
        newdate = StatsDateLib.getSecondsSinceEpoch( "%s-%s-01 00:00:00" %( year,month ) ) 
        months.append( newdate )
        #print year,month,day
    
    months.reverse()
        
    return months
  
    
      
def getYears():
    """
        Returns the last 3 year numbers including the current year.
    
    """
    
    currentTime = time.time()
    currentTime = StatsDateLib.getIsoFromEpoch( currentTime )
    currentDate = datetime.date( int(currentTime[0:4]), int(currentTime[5:7]), 1 )     
    
    years = []    

    for i in range(0,3):
        year = currentDate.year - i
        newDate = StatsDateLib.getSecondsSinceEpoch( "%s-%s-%s 00:00:00" %(year, currentDate.month, currentDate.day) )
        years.append(  newDate )
        
    years.reverse()
       
    return years   

    
        
def getCombinedMachineName( machines ):
    """
        Gets all the specified machine names
        and combines them so they can be used
        to find pickles.

    """

    combinedMachineName = ""
    splitMachines = machines.split(",")

    for machine in splitMachines:

        combinedMachineName += machine

    return combinedMachineName


            
def generateWebPage( machineTags, machineParameters, language = 'en' ):
    """
        Generates a web page based on all the 
        rxnames and tx names that have run during
        the pas x days. 
        
        Only links to available graphics will be 
        displayed.
        
    """  
    
    if language == 'fr':
        fileName = StatsPaths.STATSLANGFRBINWEBPAGES + "totalGraphicsWebPages" 
    elif language == 'en':
        fileName = StatsPaths.STATSLANGENBINWEBPAGES + "totalGraphicsWebPages"      
    
    translator = gettext.GNUTranslations(open(fileName))
    _ = translator.gettext    
    #print translator._catalog
    
    days   = getDays()
    weeks  = getWeeks()
    months = getMonths()
    years  = getYears()
    
    rxTypes      = [ _("bytecount"), _("filecount"), _("errors")]
    txTypes      = [ _("latency"), _("filesOverMaxLatency"), _("bytecount"), _("filecount"), _("errors") ]
    
    rxTypesInFileNames  = { _("bytecount"):"bytecount", _("filecount"):"filecount", _("errors"):"errors"}
    txTypesInFileNames  = { _("latency"):"latency" , _("filesOverMaxLatency"):"filesOverMaxLatency", _("bytecount"):"bytecount", _("filecount"):"filecount", _("errors"):"errors" }
    
    timeTypes    = [ _("daily"),_("weekly"),_("monthly"),_("yearly")]
    updateFrequency= { _("daily"): _("(upd. hourly)"),_("weekly"):_("(upd. hourly)"), _("monthly"):_("(upd. weekly)"),_("yearly"):_("(upd. monthly)")}  
    
    for machineTag in machineTags:
        machineNames     = machineParameters.getPairedMachinesAssociatedWithListOfTags( [ machineTag ] )
        for machineName in machineNames:
            if not os.path.isdir(StatsPaths.STATSWEBPAGESHTML):
                os.makedirs( StatsPaths.STATSWEBPAGESHTML )
            machineName = getCombinedMachineName( machineName )
            file = "%s%s_%s.html" %( StatsPaths.STATSWEBPAGESHTML, machineTag, language )
            fileHandle = open( file , 'w' )
            
            
            fileHandle.write( """ <html>         
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
                
                <STYLE>
    
                </STYLE>
                
                <style type="text/css">
                    div.left { float: left; }
                    div.right {float: right; }
                    <!--
                    A{text-decoration:none}
                    -->
                    <!--
                    td {
                        white-space: pre-wrap; /* css-3 */
    
                    }
                    // -->
                </style>    
                
                <body text="#000000" link="#FFFFFF" vlink="000000" bgcolor="#FFF4E5" >
                            
                    <h2>""" +  _("RX totals for") + ' %s'%string.upper( machineTag ) + """</h2>               
        
                <table style="table-layout: fixed; width: 100%; border-left: 0px gray solid; border-bottom: 0px gray solid; padding:0px; margin: 0px" cellspacing=10 cellpadding=6 >
                
                <tr>    
                    <td bgcolor="#006699" ><font color = "white"><div class="left">Type</font></td>   
                    
                    <td bgcolor="#006699"  title =" """  + _( "Display the total of bytes received by all sources.") + """ "><font color = "white"><div class="left">""" + _("ByteCount") + """</div><a target ="popup" href="help" onClick="wopen('helpPages/byteCount_%s.html'  """%(language)+ """ , 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                    
                    <td bgcolor="#006699"  title =" """ +_( "Display the total of files received by all sources.") + """ "><font color = "white"><div class="left">""" + _("FileCount") + """</div><a target ="popup" href="help" onClick="wopen('helpPages/fileCount_%s.html' """%(language)+ """, 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                    
                    <td bgcolor="#006699"  title =" """ +_( "Display the total of errors that occured during all the receptions.") + """ "><font color = "white"><div class="left">""" + _("Errors") + """</div><a target ="popup"  href="help" onClick="wopen('helpPages/errors_%s.html'  """%(language)+ """, 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                    
                </tr>
                   
                """   ) 
            
            
            
            for timeType in timeTypes:    
                
                fileHandle.write( """ 
                <tr> 
                    <td bgcolor="#99FF99" > %s %s</td>                  
            
                """ %(( timeType[0].upper() + timeType[1:] ), updateFrequency[timeType] ) )
                if timeType == timeTypes[0] :
                    timeContainer = days     
                elif timeType == timeTypes[1] :
                    timeContainer = weeks
                elif timeType == timeTypes[2] :
                    timeContainer = months
                elif timeType == timeTypes[3] :
                    timeContainer = years

                                 
                for type in rxTypes:
                    
                    fileHandle.write( """<td bgcolor="#66CCFF">  """ )
                    
                    for x in timeContainer:
                        year, month, day = StatsDateLib.getYearMonthDayInStrfTime( x )
                        week = time.strftime( "%W", time.gmtime(x))
                        if timeType ==  timeTypes[0] :
                            file = "%sdaily/totals/%s/rx/%s/%s/%s/%s.png" %( StatsPaths.STATSGRAPHSARCHIVES, machineName, year, month, rxTypesInFileNames[type], day )     
                            webLink =  "archives/daily/totals/%s/rx/%s/%s/%s/%s.png" %(  machineName, year, month, rxTypesInFileNames[type], day )     
                        elif timeType ==  timeTypes[1]:
                            file = "%sweekly/totals/%s/rx/%s/%s/%s.png" %(  StatsPaths.STATSGRAPHSARCHIVES, machineName, year, rxTypesInFileNames[type], week )
                            webLink ="archives/weekly/totals/%s/rx/%s/%s/%s.png" %(  machineName, year, rxTypesInFileNames[type], week )
                        elif timeType ==  timeTypes[2]:
                            file = "%smonthly/totals/%s/rx/%s/%s/%s.png" %( StatsPaths.STATSGRAPHSARCHIVES, machineName, year, rxTypesInFileNames[type], month )
                            webLink ="archives/monthly/totals/%s/rx/%s/%s/%s.png" %(  machineName, year, rxTypesInFileNames[type], month )
                        elif timeType ==  timeTypes[3]:
                            file = "%syearly/totals/%s/rx/%s/%s.png" %( StatsPaths.STATSGRAPHSARCHIVES, machineName,  rxTypesInFileNames[type], year ) 
                            webLink = "archives/yearly/totals/%s/rx/%s/%s.png" %(  machineName,  rxTypesInFileNames[type], year ) 
                        
                        
                        if os.path.isfile(file):  
 
                            if timeType == timeTypes[0] :
                                label =  time.strftime( "%a", time.gmtime(x))   
                            elif timeType == timeTypes[1]:
                                label = week
                            elif timeType == timeTypes[2]:
                                label = month
                            elif timeType == timeTypes[3]:
                                label = year   
                            fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">"""%( label, webLink ) +  "%s" %label  + """&nbsp;</a>"""  )
                      
                            
                    fileHandle.write( """</td>""" )
                
                fileHandle.write( """</tr>""" )       
                    
            fileHandle.write( """</table>""" )      
            
            ####################################txPart
            
            fileHandle.write("""                
               
                    <h2>""" + _("TX totals for") + " %s " %( string.upper( machineTag ) + """</h2>
                
                <table style="table-layout: fixed; width: 100%; border-left: 0px gray solid; border-bottom: 0px gray solid; padding:0px; margin: 0px" cellspacing=10 cellpadding=6 >
                    <tr>
                        
                        <td bgcolor="#006699"   title = ><font color = "white">Type</font></td> 
                        
                        <td bgcolor="#006699"  """ + _("Display the average latency of file transfers for all clients.") + """ "><font color = "white"><font color = "white"><div class="left">""" + _("Latency")+"""</div><a target ="popup" href="help" onClick="wopen('helpPages/latency_%s.html'"""%language + """, 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                        
                        <td bgcolor="#006699"  title =" """ + _( "Display the number of files for wich the latency was over 15 seconds for all clients.") +""" "><font color = "white"><div class="left">""" + _("Files Over Max. Lat.") + """</div><a target ="popup" href="help" onClick="wopen('helpPages/filesOverMaxLatency_%s.html'"""%language + """, 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td> 
                        
                        <td bgcolor="#006699"  title =" """ + _( "Display number of bytes transfered to all clients.") + """ "><font color = "white"><div class="left">""" +_("ByteCount") + """</div><a target ="popup" href="help" onClick="wopen('helpPages/byteCount_%s.html'"""%language + """, 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                        
                        <td bgcolor="#006699" title  =" """ + _( "Display the number of files transferred every day to all clients.") + """ "><font color = "white"><div class="left">""" + _("FileCount") + """</div><a target ="popup" href="help" onClick="wopen('helpPages/fileCount_%s.html'""" %language + """, 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                        
                        <td bgcolor="#006699"  title =" """ + _( "Display the total of errors that occured during the file transfers to allclients.") + """ "><font color = "white"><div class="left">""" + _("Errors") + """</div><a target ="popup" href="help" onClick="wopen('helpPages/errors_%s.html'"""%language + """, 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                    
                    </tr>   
                   
                """ ) )
            
            
            
            for timeType in timeTypes:    
                fileHandle.write( """ 
                <tr> 
                    <td bgcolor="#99FF99" ><div style="width:10pt";>%s %s</div> </td>                  
            
                """ %(( timeType[0].upper() + timeType[1:] ), updateFrequency[timeType] ) ) 
                if timeType == timeTypes[0] :
                    timeContainer = days     
                elif timeType == timeTypes[1]:
                    timeContainer = weeks
                elif timeType == timeTypes[2]:
                    timeContainer = months
                elif timeType == timeTypes[3]:
                    timeContainer = years
                             
                for type in txTypes:
                    
                    fileHandle.write( """<td bgcolor="#66CCFF"> """) 
                    
                    for x in timeContainer:
                        
                        year, month, day = StatsDateLib.getYearMonthDayInStrfTime( x )
                        week = time.strftime( "%W", time.gmtime(x))
                        if timeType == timeTypes[0] :
                            file = "%sdaily/totals/%s/tx/%s/%s/%s/%s.png" %( StatsPaths.STATSGRAPHSARCHIVES, machineName, year, month, txTypesInFileNames[type], day )
                            webLink = "archives/daily/totals/%s/tx/%s/%s/%s/%s.png" %( machineName, year, month, txTypesInFileNames[type], day )     
                        
                        elif timeType == timeTypes[1]:
                            file = "%sweekly/totals/%s/tx/%s/%s/%s.png" %( StatsPaths.STATSGRAPHSARCHIVES, machineName, year, txTypesInFileNames[type], week )
                            webLink = "archives/weekly/totals/%s/tx/%s/%s/%s.png" %( machineName, year, txTypesInFileNames[type], week )
                            
                        elif timeType == timeTypes[2]:
                            file = "%smonthly/totals/%s/tx/%s/%s/%s.png" %( StatsPaths.STATSGRAPHSARCHIVES, machineName, year, txTypesInFileNames[type], month )
                            webLink = "archives/monthly/totals/%s/tx/%s/%s/%s.png" %( machineName, year, txTypesInFileNames[type], month )
                            
                        elif timeType == timeTypes[3]:
                            file = "%syearly/totals/%s/tx/%s/%s.png" %( StatsPaths.STATSGRAPHSARCHIVES, machineName,  txTypesInFileNames[type], year )  
                            webLink = "archives/yearly/totals/%s/tx/%s/%s.png" %(  machineName,  txTypesInFileNames[type], year )
                        
                        if os.path.isfile(file):  
                            
                            if timeType == timeTypes[0] :
                                label =  time.strftime( "%a", time.gmtime(x))   
                            elif timeType == timeTypes[1]:
                                label = week
                            elif timeType == timeTypes[2]:
                                label = month
                            elif timeType == timeTypes[3]:
                                label = year     
                            fileHandle.write(  """<a target ="popup" href="%s" onClick="wopen('%s', 'popup', 875, 240); return false;">"""%( label, webLink ) + "%s" %str(label) + """ </a>"""  )
                        
                                 
                    fileHandle.write( """</td>""" )
                
                fileHandle.write( """</tr>""" )       
                    
            fileHandle.write( """</table>""")             
            fileHandle.write( """</body></html>""")
            #End of tx part.             
            
            fileHandle.close()         
                                
                              
   
def main():
    """
    """
    
    configParameters = StatsConfigParameters()
    configParameters.getAllParameters()
    machineParameters = MachineConfigParameters()
    machineParameters.getParametersFromMachineConfigurationFile()    
    generateWebPage( configParameters.sourceMachinesTags, machineParameters )
     
    
if __name__ == "__main__":
    main()            
            
            
            
            
            
            
    
             