#! /usr/bin/env python
"""
##############################################################################
##
##
## @name     : DailyGraphicsWebPageGenerator.py 
##
##
## @author:  : Nicholas Lemay
##
## @license  : MetPX Copyright (C) 2004-2006  Environment Canada
##             MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
##             named COPYING in the root of the source directory tree. 
##
## @since    :  2006-11-22, last updated on 2008-02-19
##
##
## @summary : Generates a web pages that gives access to user 
##               to the daily graphics of the last 7 days for all 
##               rx sources and tx clients.
##
##
##############################################################################
"""


"""
    Small function that adds pxlib to the environment path.  
"""
import  os, time, sys


sys.path.insert(1,  os.path.dirname( os.path.abspath(__file__) ) + '/../../')
"""
    Imports
    PXManager requires pxlib 
"""
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.WebPageGeneratorInterface import WebPageGeneratorInterface
from pxStats.lib.StatsConfigParameters import StatsConfigParameters


# Constants
LOCAL_MACHINE = os.uname()[1]
CURRENT_MODULE_ABS_PATH =  os.path.abspath(__file__).replace( ".pyc", ".py" )          
NB_DAYS_DISPLAYED = 7 
    


class DailyGraphicsWebPageGenerator( WebPageGeneratorInterface ):    
    
    
    
    def __init__( self, displayedLanguage = 'en', filesLanguage='en', days = None, \
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
                
        self.displayedLanguage = displayedLanguage
        self.filesLanguage     = filesLanguage
       
        self.pathsTowardsGraphics = StatsPaths()
        self.pathsTowardsGraphics.setPaths( filesLanguage )
        
        self.pathsTowardsOutputFiles = StatsPaths()
        self.pathsTowardsOutputFiles.setPaths( self.displayedLanguage )
        


    def setDays( self ):
        """
            @Summary : Sets the days value to an array containing
                      the last X days in "since epoch" numbers
                      based on the globally set NB_DAYS_DISPLAYED
                      value.
        
        """
        
        days = []
        
        startTime = ( time.time() - (NB_DAYS_DISPLAYED*24*60*60) )
        for i in range( 1, NB_DAYS_DISPLAYED + 1 ):
            days.append( ( startTime + ( i*24*60*60 ) ) )   
           
        self.days = days
    
    
    
    def getStartEndOfWebPage():
        """
            @summary : Returns the time of the first 
                       graphics to be shown on the web 
                       page and the time of the last 
                       graphic to be displayed. 
            @return : Start,end tuple both in ISO format. 
        """
        
        currentTime = StatsDateLib.getIsoFromEpoch( time.time() )  
        
        start = StatsDateLib.rewindXDays( currentTime, NB_DAYS_DISPLAYED - 1 )
        start = StatsDateLib.getIsoTodaysMidnight( start )
             
        end   = StatsDateLib.getIsoTodaysMidnight( currentTime )
            
        return start, end 
    
    getStartEndOfWebPage = staticmethod( getStartEndOfWebPage )    


    
    def printWebPage( self, rxNames, txNames ):
        """
            @summary : Prints out a daily web page
                       with the content based on 
                       the specified parameters.
            
            @param rxNames: List of rx for which to display the graphics
            
            @param txNames: List of rx for which to display the graphics
            
            @precondition: global _ translator must be set prior to calling this function.
             
            @note :   Only links to available graphics will be 
                      displayed.
            
        """  
        
        global _ 
        
        rxNamesArray = rxNames.keys()
        txNamesArray = txNames.keys()
        
        rxNamesArray.sort()
        txNamesArray.sort()
        
        #Redirect output towards html page to generate.    
        if not os.path.isdir( self.pathsTowardsOutputFiles.STATSWEBPAGESHTML ):
            os.makedirs( self.pathsTowardsOutputFiles.STATSWEBPAGESHTML )
        
        fileHandle = open( self.pathsTowardsOutputFiles.STATSWEBPAGESHTML  +"dailyGraphs_%s.html" %self.displayedLanguage , 'w' )
    
         
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
    
                var descriptionWindow=dhtmlwindow.open("description", "inline", "description", "Description", "width=900px,height=120px,left=150px,top=10px,resize=1,scrolling=0", "recal")
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
                       var sourceHelpPage = dhtmlwindow.open("sourceHelpPage", "iframe", "helpPages/source_%s.html", "Definition of 'source'", "width=875px,height=100px,resize=1,scrolling=1,center=1", "recal")
                       sourceHelpPage.moveTo("middle", "middle"); 
                    }""" %(self.displayedLanguage) + """
                    
                    
                    function showClientHelpPage(){
                       var clientHelpPage = dhtmlwindow.open("client", "iframe", "helpPages/client_%s.html", "Definition of 'client'", "width=875px,height=150px,resize=1,scrolling=1,center=1", "recal")
                        .moveTo("middle", "middle");
                    }""" %(self.displayedLanguage) + """
                    
            </script>
            
             
            <STYLE>
                <!--
                A{text-decoration:none}
                -->
            </STYLE>
            
            
            <style type="text/css">
                div.left { float: left; }
                div.right {float: right; }
            </style>
        
            
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
            
                <h2>""" + _( "Daily graphics for RX sources from MetPx.") + """ <font size = "2">""" + _("*updated hourly") + """</font></h2>
            
                <div class="tableContainer">         
                   <table> 
                       <thead>
            
                            <tr>    
                                <td bgcolor="#006699">
                                    <div class = "rxTableEntry">
                                        <font color = "white">
                                            <center>
                                                    Sources
                                                    <br>
                                                    <a target ="popup" href="#" onClick="showSourceHelpPage(); return false;">
                                                    ?
                                                    </a>
                                            </center>
                                        </font>
                                    </div>
                                </td>
                                
                                <td bgcolor="#006699">
                                    <font color = "white">""" + _("List of available daily graphics.") + """</font>                                
                                </td>
                            </tr>   
                        </thead>
            
            
                        <tbody>
        
        """)
        
        
        
        for rxName in rxNamesArray :
            
            if rxNames[rxName] == "" :
                fileHandle.write( """<tr> <td bgcolor="#99FF99"> %s</td> """ %(rxName))
                fileHandle.write( """<td bgcolor="#66CCFF"> """ + _("Days") + """ :   """ )
            else:
                machineName = self.getMachineNameFromDescription( self.getMachineNameFromDescription( rxNames[rxName] ) )
                fileHandle.write( """<tr> <td bgcolor="#99FF99"><div class="left"> %s</div><div class="right"><a href="#" onClick="descriptionWindow.load('inline', '%s', 'Description');descriptionWindow.show(); return false"><font color="black">?</font></a></div><br>(%s)</td> """ %(rxName, rxNames[rxName].replace("'","").replace('"','').replace( ",", ", "), machineName ) )
                fileHandle.write( """<td bgcolor="#66CCFF"> """ + _("Days") + """ :   """ )
                
                    
            for day in self.days:
                
                currentYear, currentMonth, currentDay = StatsDateLib.getYearMonthDayInStrfTime( day )
                
                _ = self.getTranslatorForModule( CURRENT_MODULE_ABS_PATH, self.filesLanguage)
                
                file = file = self.pathsTowardsGraphics.STATSGRAPHSARCHIVES + _("daily/rx/%s/")%( rxName ) + str(currentYear) + "/" + str(currentMonth) + "/" + str(currentDay) + ".png"
                webLink = _("archives/daily/rx/%s/")%( rxName ) + str(currentYear) + "/" + str(currentMonth) + "/" + str(currentDay) + ".png"
                
                _ = self.getTranslatorForModule( CURRENT_MODULE_ABS_PATH, self.displayedLanguage )
                
                if os.path.isfile( file ):
                    fileHandle.write(  """<a target ="%s" href="%s">"""%( rxName, webLink) + "%s" %time.strftime( "%a", time.gmtime(day) )  + """   </a>""" )
                    
                     
            fileHandle.write( """</td></tr>""" )
        
        fileHandle.write( """
        
                </tbody>
            </table>
        </div>
           
        <h2>""" + _("Daily graphics for TX clients from MetPx.") + """ <font size = "2">""" +_("*updated hourly") + """</font></h2>
        
        <div class="tableContainer">         
            <table> 
                <thead>
                    <tr>
    
                         <td bgcolor="#006699">
                            <div class = "txTableEntry">
                                <font color = "white">
                                    <center>
                                        Clients
                                        <br>
                                        <a target ="popup" href="#" onClick="showClientHelpPage(); return false;">                                        
                                          ?
                                        </a>
                                    <center>
                                </font>
                            </div>
                        </td>
                        
                        <td bgcolor="#006699">
                            <div class = "txTableEntry">
                                <font color = "white">""" + _("List of available daily graphics.") + """</font>
                            </div>    
                        </td>
                
                    </tr>  
             </thead>   
         
         
            <tbody> 
        
           
        """   )       
            
            
            
        for txName in txNamesArray :           
            
            if txNames[txName] == "" :
                fileHandle.write( """<tr> <td bgcolor="#99FF99"> %s</td> """ %(txName))
                fileHandle.write( """<td bgcolor="#66CCFF"><div class = "txTableEntry">   """ + _("Days") + """ :   """ )
            else:
                machineName = self.getMachineNameFromDescription( txNames[txName] ) 
                fileHandle.write( """<tr> <td bgcolor="#99FF99"><div class="left"> %s </div><div class="right"><a href="#" onClick="descriptionWindow.load('inline', '%s', 'Description');descriptionWindow.show(); return false"><font color="black">?</font></a></div><br>(%s)</td> """ %(txName, txNames[txName].replace("'","").replace('"','').replace(",", ", "), machineName ))
                fileHandle.write( """<td bgcolor="#66CCFF">  """ + _("Days") + """ :   """ )
            
            
            for day in self.days:
                            
                currentYear, currentMonth, currentDay = StatsDateLib.getYearMonthDayInStrfTime( day )
                
                _ = self.getTranslatorForModule( CURRENT_MODULE_ABS_PATH, self.filesLanguage )
                
                file = self.pathsTowardsGraphics.STATSGRAPHSARCHIVES + _("/daily/tx/%s/")%( txName ) + str(currentYear) + "/" + str(currentMonth) + "/" + str(currentDay) + ".png"
                webLink =  _("archives/daily/tx/%s/")%( txName ) + str(currentYear) + "/" + str(currentMonth) + "/" + str(currentDay) + ".png"

                _ = self.getTranslatorForModule( CURRENT_MODULE_ABS_PATH, self.displayedLanguage )

                if os.path.isfile( file ):
                    fileHandle.write(  """<a target ="%s" href="%s">"""%( rxName, webLink) + "%s" %(time.strftime( "%a", time.gmtime(day)) )+"""  </a>""" )    
    
            fileHandle.write( "</td></tr>" )
    
        fileHandle.write(  """
          
              </tbody>
        
          </table>    
           
        </body>
    
    </html>
        
        
        
        """ )       
                    
        fileHandle.close()                 
        
        
        
    def generateWebPage( self ):
        """
        
            @summary : Call to generate the web page. 
            
        """
        
        self.setDays()
        start, end = self.getStartEndOfWebPage()
        rxNames, txNames = GeneralStatsLibraryMethods.getRxTxNamesForWebPages( start, end )
        self.printWebPage( rxNames, txNames )
        
    
