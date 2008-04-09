#! /usr/bin/env python
"""
##############################################################################
##
##
## @Name   : totalGraphicsWebPages.py 
##
## 
## Author : Nicholas Lemay
##
## 
## @license : MetPX Copyright (C) 2004-2006  Environment Canada
##            MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
##            named COPYING in the root of the source directory tree.
##
## @since   : 25-01-2007, last updated on 08-04-2008 
##
##
## @summary :    Generates the web pages that gives access to users
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

"""
    - Add pxStats to sys.path
"""
sys.path.insert(1, os.path.dirname( os.path.abspath(__file__) ) + '/../../../')
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.StatsConfigParameters import StatsConfigParameters
from pxStats.lib.MachineConfigParameters import MachineConfigParameters
from pxStats.lib.WebPageGeneratorInterface import WebPageGeneratorInterface


"""
    - Add pxlib to sys.path
"""
STATSPATHS = StatsPaths()
STATSPATHS.setPaths()
sys.path.append(STATSPATHS.PXLIB)


"""
    Imports
    PXManager requires pxlib 
"""
from PXManager import *

   
LOCAL_MACHINE = os.uname()[1]   
CURRENT_MODULE_ABS_PATH =  os.path.abspath(__file__).replace( ".pyc", ".py" )



class TotalsGraphicsWebPageGenerator( WebPageGeneratorInterface ): 

    def __init__( self, displayedLanguage = 'en', filesLanguage='en', days = None, \
                  weeks = None, months = None, years = None, \
                  pathsTowardsGraphics = None, pathsTowardsOutputFiles = None  ):
        """
        
            @summary : Constructor 
            
            @param displayedLanguage: Languages in which to display 
                                      the different captions found within 
                                      the generated web page.  
            
            @param fileLanguages: Language in which the files that 
                                  will be referenced within this page
                                  have been generated.
                                  
            @param days : List of days that the web page covers.
        
            @note : Will set two global translators to be used throughout this module 
                    _ which translates every caption that is to be printed.
                    _F which translates every filename that is to be linked.     
        """
        
        configParameters = StatsConfigParameters()
        configParameters.getGeneralParametersFromStatsConfigurationFile()
      
        global _ 
        _ =  self.getTranslatorForModule( CURRENT_MODULE_ABS_PATH, displayedLanguage )
        
        if days == None:
            self.setDays()
        else:    
            self.days = days 
            
        if weeks == None:
            self.setWeeks()
        else:    
            self.weeks = weeks             
            
        if months == None:
            self.setMonths()
        else:    
            self.months = months 
                            
        if years == None:
            self.setYears()
        else:    
            self.years = years                 
                
        self.displayedLanguage = displayedLanguage
        self.filesLanguage     = filesLanguage
       
        self.pathsTowardsGraphics = StatsPaths()
        self.pathsTowardsGraphics.setPaths( filesLanguage )
        
        self.pathsTowardsOutputFiles = StatsPaths()
        self.pathsTowardsOutputFiles.setPaths( self.displayedLanguage )

        StatsDateLib.setLanguage(filesLanguage)

    def setDays( self ):
        """
            Returns the last 5 days numbers including the current year.
        
        """
        
        days = []
        
        startTime = (time.time() - (7*24*60*60))
        for i in range(1,8):
            days.append( startTime + ( i*24*60*60 ) )
       
           
        self.days = days
        
    
        
    def setWeeks( self ):
        """
            Returns the 5 week numbers including current week number.
        
        """
        
        weeks = []
        
        startTime = (time.time() - (5*7*24*60*60))
        for i in range(1,6):
            weeks.append( startTime + (i*7*24*60*60) )
       
        self.weeks =  weeks
        
        
        
    def setMonths( self ):
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
                
           
            newdate = StatsDateLib.getSecondsSinceEpoch( "%s-%s-01 00:00:00" %( year,month ) ) 
            months.append( newdate )
            #print year,month,day
        
        months.reverse()
            
        self.months = months
      
        
          
    def setYears( self ):
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
           
        self.years =  years   

    
        
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

    getCombinedMachineName = staticmethod( getCombinedMachineName )

            
            
    def printWebPage( self, machineTags, machineParameters ):
        """
            Generates a web page based on all the 
            rxnames and tx names that have run during
            the pas x days. 
            
            Only links to available graphics will be 
            displayed.
            
        """  
        
        global _
      
        rxTypes      = [ _("bytecount"), _("filecount"), _("errors")]
        txTypes      = [ _("latency"), _("filesOverMaxLatency"), _("bytecount"), _("filecount"), _("errors") ]
        
        rxTypesInFileNames  = { _("bytecount"):"bytecount", _("filecount"):"filecount", _("errors"):"errors"}
        txTypesInFileNames  = { _("latency"):"latency" , _("filesOverMaxLatency"):"filesOverMaxLatency", _("bytecount"):"bytecount", _("filecount"):"filecount", _("errors"):"errors" }
        
        timeTypes    = [ _("daily"),_("weekly"),_("monthly"),_("yearly")]
        updateFrequency= { _("daily"): _("(upd. hourly)"),_("weekly"):_("(upd. hourly)"), _("monthly"):_("(upd. weekly)"),_("yearly"):_("(upd. monthly)")}  
        
        for machineTag in machineTags:
            machineNames     = machineParameters.getPairedMachinesAssociatedWithListOfTags( [ machineTag ] )
            for machineName in machineNames:
                if not os.path.isdir(self.pathsTowardsGraphics.STATSWEBPAGESHTML):
                    os.makedirs( self.pathsTowardsOutputFiles.STATSWEBPAGESHTML )
                machineName = TotalsGraphicsWebPageGenerator.getCombinedMachineName( machineName )
                file = "%s%s_%s.html" %( self.pathsTowardsOutputFiles.STATSWEBPAGESHTML, machineTag, self.displayedLanguage )
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
                        
                        <td bgcolor="#006699"  title =" """  + _( "Display the total of bytes received by all sources.") + """ "><font color = "white"><div class="left">""" + _("ByteCount") + """</div><a target ="popup" href="help" onClick="wopen('helpPages/byteCount_%s.html'  """%(self.displayedLanguage)+ """ , 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                        
                        <td bgcolor="#006699"  title =" """ +_( "Display the total of files received by all sources.") + """ "><font color = "white"><div class="left">""" + _("FileCount") + """</div><a target ="popup" href="help" onClick="wopen('helpPages/fileCount_%s.html' """%(self.displayedLanguage)+ """, 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                        
                        <td bgcolor="#006699"  title =" """ +_( "Display the total of errors that occured during all the receptions.") + """ "><font color = "white"><div class="left">""" + _("Errors") + """</div><a target ="popup"  href="help" onClick="wopen('helpPages/errors_%s.html'  """%(self.displayedLanguage)+ """, 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                        
                    </tr>
                       
                    """   ) 
                
                
                
                for timeType in timeTypes:    
                    
                    fileHandle.write( """ 
                    <tr> 
                        <td bgcolor="#99FF99" > %s %s</td>                  
                
                    """ %(( timeType[0].upper() + timeType[1:] ), updateFrequency[timeType] ) )
                    if timeType == timeTypes[0] :
                        timeContainer = self.days     
                    elif timeType == timeTypes[1] :
                        timeContainer = self.weeks
                    elif timeType == timeTypes[2] :
                        timeContainer = self.months
                    elif timeType == timeTypes[3] :
                        timeContainer = self.years
    
                                     
                    for type in rxTypes:
                        
                        fileHandle.write( """<td bgcolor="#66CCFF">  """ )
                        
                        for x in timeContainer:
                            year, month, day = StatsDateLib.getYearMonthDayInStrfTime( x )
                            week = time.strftime( "%W", time.gmtime(x))
                            if timeType ==  timeTypes[0] :
                                file = "%sdaily/totals/%s/rx/%s/%s/%s/%s.png" %( self.pathsTowardsGraphics.STATSGRAPHSARCHIVES, machineName, year, month, rxTypesInFileNames[type], day )     
                                webLink =  "archives/daily/totals/%s/rx/%s/%s/%s/%s.png" %(  machineName, year, month, rxTypesInFileNames[type], day )     
                            elif timeType ==  timeTypes[1]:
                                file = "%sweekly/totals/%s/rx/%s/%s/%s.png" %(  self.pathsTowardsGraphics.STATSGRAPHSARCHIVES, machineName, year, rxTypesInFileNames[type], week )
                                webLink ="archives/weekly/totals/%s/rx/%s/%s/%s.png" %(  machineName, year, rxTypesInFileNames[type], week )
                            elif timeType ==  timeTypes[2]:
                                file = "%smonthly/totals/%s/rx/%s/%s/%s.png" %( self.pathsTowardsGraphics.STATSGRAPHSARCHIVES, machineName, year, rxTypesInFileNames[type], month )
                                webLink ="archives/monthly/totals/%s/rx/%s/%s/%s.png" %(  machineName, year, rxTypesInFileNames[type], month )
                            elif timeType ==  timeTypes[3]:
                                file = "%syearly/totals/%s/rx/%s/%s.png" %( self.pathsTowardsGraphics.STATSGRAPHSARCHIVES, machineName,  rxTypesInFileNames[type], year ) 
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
                            
                            <td bgcolor="#006699"  """ + _("Display the average latency of file transfers for all clients.") + """ "><font color = "white"><font color = "white"><div class="left">""" + _("Latency")+"""</div><a target ="popup" href="help" onClick="wopen('helpPages/latency_%s.html'"""%self.displayedLanguage + """, 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                            
                            <td bgcolor="#006699"  title =" """ + _( "Display the number of files for wich the latency was over 15 seconds for all clients.") +""" "><font color = "white"><div class="left">""" + _("Files Over Max. Lat.") + """</div><a target ="popup" href="help" onClick="wopen('helpPages/filesOverMaxLatency_%s.html'"""%self.displayedLanguage + """, 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td> 
                            
                            <td bgcolor="#006699"  title =" """ + _( "Display number of bytes transfered to all clients.") + """ "><font color = "white"><div class="left">""" +_("ByteCount") + """</div><a target ="popup" href="help" onClick="wopen('helpPages/byteCount_%s.html'"""%self.displayedLanguage + """, 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                            
                            <td bgcolor="#006699" title  =" """ + _( "Display the number of files transferred every day to all clients.") + """ "><font color = "white"><div class="left">""" + _("FileCount") + """</div><a target ="popup" href="help" onClick="wopen('helpPages/fileCount_%s.html'""" %self.displayedLanguage + """, 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                            
                            <td bgcolor="#006699"  title =" """ + _( "Display the total of errors that occured during the file transfers to allclients.") + """ "><font color = "white"><div class="left">""" + _("Errors") + """</div><a target ="popup" href="help" onClick="wopen('helpPages/errors_%s.html'"""%self.displayedLanguage + """, 'popup', 875, 100); return false;"><div class="right">?</div></a></font></td>
                        
                        </tr>   
                       
                    """ ) )
                
                
                
                for timeType in timeTypes:    
                    fileHandle.write( """ 
                    <tr> 
                        <td bgcolor="#99FF99" ><div style="width:10pt";>%s %s</div> </td>                  
                
                    """ %(( timeType[0].upper() + timeType[1:] ), updateFrequency[timeType] ) ) 
                    if timeType == timeTypes[0] :
                        timeContainer = self.days     
                    elif timeType == timeTypes[1]:
                        timeContainer = self.weeks
                    elif timeType == timeTypes[2]:
                        timeContainer = self.months
                    elif timeType == timeTypes[3]:
                        timeContainer = self.years
                                 
                    for type in txTypes:
                        
                        fileHandle.write( """<td bgcolor="#66CCFF"> """) 
                        
                        for x in timeContainer:
                            
                            year, month, day = StatsDateLib.getYearMonthDayInStrfTime( x )
                            week = time.strftime( "%W", time.gmtime(x))
                            if timeType == timeTypes[0] :
                                file = "%sdaily/totals/%s/tx/%s/%s/%s/%s.png" %( self.pathsTowardsGraphics.STATSGRAPHSARCHIVES, machineName, year, month, txTypesInFileNames[type], day )
                                webLink = "archives/daily/totals/%s/tx/%s/%s/%s/%s.png" %( machineName, year, month, txTypesInFileNames[type], day )     
                            
                            elif timeType == timeTypes[1]:
                                file = "%sweekly/totals/%s/tx/%s/%s/%s.png" %( self.pathsTowardsGraphics.STATSGRAPHSARCHIVES, machineName, year, txTypesInFileNames[type], week )
                                webLink = "archives/weekly/totals/%s/tx/%s/%s/%s.png" %( machineName, year, txTypesInFileNames[type], week )
                                
                            elif timeType == timeTypes[2]:
                                file = "%smonthly/totals/%s/tx/%s/%s/%s.png" %( self.pathsTowardsGraphics.STATSGRAPHSARCHIVES, machineName, year, txTypesInFileNames[type], month )
                                webLink = "archives/monthly/totals/%s/tx/%s/%s/%s.png" %( machineName, year, txTypesInFileNames[type], month )
                                
                            elif timeType == timeTypes[3]:
                                file = "%syearly/totals/%s/tx/%s/%s.png" %( self.pathsTowardsGraphics.STATSGRAPHSARCHIVES, machineName,  txTypesInFileNames[type], year )  
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
                                
                

    def generateWebPage( self ):
        """
            @summary :           
            
        
        """
        
        configParameters = StatsConfigParameters()
        configParameters.getAllParameters()
        machineParameters = MachineConfigParameters()
        machineParameters.getParametersFromMachineConfigurationFile()    
        self.printWebPage( configParameters.sourceMachinesTags, machineParameters )
                
           
            
            
            
            
            
            
    
             