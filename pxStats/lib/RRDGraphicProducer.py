#! /usr/bin/env python

"""
#############################################################################################
#
#
# Name: RRDGraphicProducer.py
#
# @author: Nicholas Lemay
#
# @since: 2008-01-30
#
#
# @license: MetPX Copyright (C) 2004-2007  Environment Canada
#           MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
#           named COPYING in the root of the source directory tree.
#
# Description : This class is to be used to plot RRDGraphics.  
#
# 
#############################################################################################
"""

import commands, gettext, os, time, getopt, rrdtool, shutil, sys


"""
    Small function that adds pxStats to the environment path.  
"""
sys.path.insert(1, sys.path[0] + '/../../')

from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.RrdUtilities import RrdUtilities
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.StatsPaths import StatsPaths  
from pxStats.lib.LanguageTools import LanguageTools
from pxStats.lib.Translatable import Translatable


"""
    - Small function that adds pxLib to sys path.
"""
statsPaths = StatsPaths( )
statsPaths.setBasicPaths()
sys.path.append( statsPaths.PXLIB )

from   Logger import *

CURRENT_MODULE_ABS_PATH = os.path.abspath( sys.path[0] ) + '/' + "RRDGraphicProducer.py"     


class RRDGraphicProducer( Translatable ):

    def __init__( self, fileType, types, totals, graphicType, clientNames = None ,\
                  timespan = 12, startTime = None, endTime = None, machines = ["machine1"],\
                  copy = False, mergerType = "", turnOffLogging = False, 
                  inputLanguage = "", outputLanguage = ""  ):            
        
        
        self.fileType     = fileType          # Type of log files to be used.    
        self.types        = types             # Type of graphics to produce. 
        self.clientNames  = clientNames or [] # Client name we need to get the data from.
        self.timespan     = timespan          # Number of hours we want to gather the data from.
        self.startTime    = startTime         # Time where graphic(s) starts 
        self.endTime      = endTime           # Time where graphic(s) ends.
        self.machines     = machines          # Machine from wich we want the data to be calculated.
        self.totals       = totals            # Make totals of all the specified clients 
        self.copy         = copy              # Whether or not to create copies of the images. 
        self.graphicType  = graphicType       # daily, weekly, monthly yearly or other                
        self.mergerType   = mergerType        # Type of merger either "" for none or totalForMachine or group  
        self.turnOffLogging =turnOffLogging   # Whether to turn off logging or not 
        self.inputLanguage = inputLanguage    # Language in which the partameters will be written.
        
        if outputLanguage == "":
            self.outputLanguage = LanguageTools.getMainApplicationLanguage()
        else:
            self.outputLanguage = outputLanguage
        
        self.pathTowardsSourceFiles = StatsPaths()
        self.pathTowardsProducedGraphics = StatsPaths()
        
        self.pathTowardsSourceFiles.setPaths( LanguageTools.getMainApplicationLanguage() )
        self.pathTowardsProducedGraphics.setPaths(outputLanguage)
        
        if turnOffLogging == False:
            logger = Logger( statsPaths.STATSLOGGING + 'stats_'+'rrd_graphs' + '.log.notb', 'INFO', 'TX' + 'rrd_graphs', bytes = 10000000  ) 
            self.logger = logger.getLogger()
        else:
            self.logger = None
        
        self.translatorForOutput = self.getTranslatorForModule( CURRENT_MODULE_ABS_PATH, self.outputLanguage )
        self.translatorForInput  = self.getTranslatorForModule( CURRENT_MODULE_ABS_PATH, self.inputLanguage )
        
            
    
    def buildTitle( self, type, client,  minimum, maximum, mean):
        """
            @summary : Returns the title of the graphic based on infos. 
            
            @param type:
            
            @param client:
            
            @param endTime:
            
            @param timespan:
            
            @param minimum:
            
            @param maximum:
            
            @param mean:
    
            @return:  Returns the title of the graphic based on infos.
        
        """    
        
        _ = self.translatorForOutput
        
        span        = self.timespan
        timeMeasure = _("hours")
        
        if span%(365*24) == 0 :
            span = span/(365*24)
            timeMeasure = _("year(s)" )
        
        elif span%(30*24) == 0 :
            span = span/(30*24)
            timeMeasure = _("month(s)") 
        
        elif span%24 == 0 :
            span = span/24
            timeMeasure = _( "day(s)" )
        
        type = type[0].upper() + type[1:]    
    
        
        return  "%s "%type + _("for") +" %s "%(client) + _("for a span of ") + "%s %s "%( span, timeMeasure ) + _("ending at") + " %s."%( self.endTime )    
    
        
        
    def getGraphicsNote( self, interval, type ):
        """
            @summary : Returns the note to be displayed at the bottom of the graphic.
            @param interval:
            @param type:
            @return : Returns the note to be displayed at the bottom of the graphic.
        """
        
        _ = self.translatorForInput
        
        graphicsNote = ""
        
        if type != _("latency"):
            
            _ = self.translatorForOutput #Note is based on output language....
            
            if interval < 60 :    
                graphicsNote = _("Graphics generated using ") + str(int(interval)) + " " + _( "minute(s) averages.")
            
            else:    
                graphicsNote =_("Graphics generated using ") + str( int(interval/60) ) + " " + _("hour(s) averages.")
    
        
        return graphicsNote    
            
                 
                          
    def getAbsoluteMin( databaseName, startTime, endTime, logger = None ):
        """
            @summary : This methods returns the minimum of the entire
                       set of data found between startTime and endTime
                       within the specified database name.
            
                       In most case this will be a different min than
                       the visible min found on the graphic since the
                       drawn points usually show the total or average of 
                       numerous data entries.
            
            @return : The absolute minimum
        """
        
        
        minimum = None 
        
        try :  
        
            output = rrdtool.fetch( databaseName, 'MIN', '-s', "%s" %(startTime + 60 ), '-e', '%s' %endTime )
            minTuples = output[2]
            
            i = 0 
            while i < len( minTuples ):
                if minTuples[i][0] != 'None' and minTuples[i][0] != None  :       
                                    
                    if minTuples[i][0] < minimum or minimum == None : 
                        minimum = minTuples[i][0]
                        
                i = i + 1 
           
             
        except :
        
            if logger != None:
                try:
                    logger.error( _("Error in generateRRDGraphics.getOverallMin. Unable to read " ) + str(databaseName) )
                except:
                    pass    
            pass    
            
        return minimum
        
    getAbsoluteMin = staticmethod( getAbsoluteMin )    
        
        
        
    def getAbsoluteMax( databaseName, startTime, endTime, logger = None ):
        """
            @summary : This methods returns the max of the entire set
                       of data found between startTime and endTime 
                       within the specified database name.        
                       
                       In most case this will be a different max than
                       the visible max found on the graphic since the
                       drawn points usually show the total or average of 
                       numerous data entries.
            
            @param databaseName:
            
            @param startTime:
            
            @param endTime:
            
            @param logger:
        
            @return : The absolute max 
        """  
        
        maximum = None
        
        try:
        
            output = rrdtool.fetch( databaseName, 'MAX', '-s', "%s" %(startTime) , '-e', '%s' %endTime )      
            
            maxTuples = output[2]
            
            for maxTuple in maxTuples :
                if maxTuple[0] != 'None' and maxTuple[0] != None :
                    if maxTuple[0] > maximum : 
                        maximum = maxTuple[0]
    
        
        except :
            if logger != None:
                try:
                    logger.error( _("Error in generateRRDGraphics.getOverallMin. Unable to read ") + str( databaseName ) )
                except:
                    pass    
            pass    
        
        return maximum 
     
    getAbsoluteMax = staticmethod( getAbsoluteMax )    
           
    def getAbsoluteMean( databaseName, startTime, endTime, logger = None  ):
        """
            @summary : This methods returns the mean of the entire set
                       of data found between startTime and endTime 
                       within the specified database name.
            
                      In most case this will be a different mean 
                      than the visible mean found on the graphic since
                      the drawn points usually show the total or
                      average of numerous data entries.
             
            @param databaseName:
            
            @param startTime:
            
            @param endTime:
            
            @param logger:
             
            @return : the absolute mean.
            
        """
        
        sum = 0 
        avg = 0
        
        try :
            
            output = rrdtool.fetch( databaseName, 'AVERAGE', '-s', "%s" %(startTime + 60 ), '-e', '%s' %endTime )
    
            meanTuples = output[2]
            i = 0
            for meanTuple in meanTuples :            
                if meanTuple[0] != 'None' and meanTuple[0] != None :
                    sum = sum + meanTuple[0]
                    i = i + 1         
            
            avg = sum / len( meanTuples )  
            
        
        except :
            if logger != None:
                try:
                    logger.error( _( "Error in generateRRDGraphics.getOverallMin. Unable to read ") + str(databaseName) )
                except:
                    pass    
            pass    
                
        return avg 
    
    getAbsoluteMean = staticmethod( getAbsoluteMean )
    
    
        
    def fetchDataFromRRDDatabase( databaseName, startTime, endTime, interval, graphicType):
        """
            @summary : Returns the stored data from a database based
                       on the desiered interval.
        
        
            @param databaseName:
            
            @param startTime:
            
            @param endTime:
            
            @param interval:
            
            @param graphicType:
           
            @return :  Returns the stored data from a database based 
            on the desiered interval.
        
        """
        
        resolution = int(interval*60)
        
        if endTime > ( time.time() )/3600*3600:
            endTime = int(time.time())/3600*3600 #top of the hour...databases are never any newer
            
        # round end time to time closest to desired resolution EX : closest 10 minutes,hour,day,etc... 
        endTime = int(endTime)/int(resolution)*int(resolution)
              
        
        try:
            output = rrdtool.fetch( databaseName, 'AVERAGE', '-r', str(resolution), '-s', "%s" %(startTime), '-e', '%s' %(endTime) )
            #print databaseName, 'AVERAGE', '-r', str(resolution), '-s', "%s" %(startTime), '-e', '%s' %(endTime)
        
        except:
            output = ""
            #------------- print "Error.Could not fetch data from %s." %databaseName
            #------------------------------------------- print "Program terminated."
            #------------------------------------------------------------ sys.exit()
            
        
        return output 
        
    fetchDataFromRRDDatabase = staticmethod( fetchDataFromRRDDatabase )    
        
        
        
    def getGraphicsMinMaxMeanTotal( self, databaseName, startTime, endTime, dataInterval, desiredInterval = None,  type="average" ):
        """
            @summary : This methods returns the min max and mean of 
                       the entire set of data that is drawn on 
                       the graphic.
            
            @param databaseName:
            
            @param startTime:
            
            @param endTime:
            
            @param graphicType:
            
            @param dataInterval:
            
            @param desiredInterval:
            
            @param type:
            
            @param logger:
                   
            @return : the min, max, avg, total of the graphic
        """
        
        min = None
        max = None
        sum = 0.0
        avg = 0
        total = 0.0
        nbEntries = 0    
        nbEntriesPerPoint =1    
        
        if desiredInterval == None :
            desiredInterval = dataInterval
            
        if endTime > ( time.time()/3600 * 3600 ):
            realEndTime = int(time.time())/3600 * 3600 # round to start of hour, wich should be last update... 
        else :
            realEndTime = endTime    
            
        output = RRDGraphicProducer.fetchDataFromRRDDatabase( databaseName, startTime, endTime, dataInterval, self.graphicType )  
        
        
        if output != "":
        
            meanTuples = output[2]
            nbEntries = len( meanTuples )-1 #we dont use the first entry
                            
            desiredNumberOfEntries = float( (realEndTime - startTime)/(desiredInterval*60) )
              
            #print "nbEntries %s desiredNumberOfEntries %s" %( nbEntries, desiredNumberOfEntries )
            if nbEntries > desiredNumberOfEntries:
                nbEntriesPerPoint = int( nbEntries/desiredNumberOfEntries )
                nbEntries = desiredNumberOfEntries
                        
                
            if type == "totals":
                
                for i in range( 1,len(meanTuples),1 ) :            
                    
                    if meanTuples[i][0] != 'None' and meanTuples[i][0] != None :
                        
                        realValue = ( float(meanTuples[i][0]) * float(dataInterval)/ nbEntriesPerPoint ) 
                        
                        if  realValue > max:
                            max = realValue
                        if realValue < min or min == None :
                            min = realValue 
                        
                        sum = sum + realValue 
                        
                    else:# don't count non-filled entries in mean.
                        nbEntries = nbEntries - 1
                            
                if nbEntries != 0:            
                    avg = sum / nbEntries 
                
                
                total = sum
                    
            else:
                
                
                for i in range( int(nbEntriesPerPoint)+1 ,( len(meanTuples) ), int(nbEntriesPerPoint) ) : 
                    
                    if nbEntriesPerPoint != 1:           
                        value = None
                        nbInvalidEntries = 0 
                                       
                        for j in range( i-int(nbEntriesPerPoint), i, 1):                    
                            if meanTuples[j][0] != 'None' and meanTuples[j][0] != None :
                                if value == None :
                                    value = 0.0
                                value = value + float( meanTuples[j][0] )
                                                             
                            else:# don't count non-filled entries in mean.
                                 
                                nbInvalidEntries = nbInvalidEntries + 1
                                                
                        if nbInvalidEntries == nbEntriesPerPoint:
                            
                            nbEntries = nbEntries - 1 
                        
                        if value != None :                    
                            value = float( float(value)/ float(nbEntriesPerPoint) )
                            
                            if  value > max:
                                max = value
                            if value < min or min == None :
                                min = value 
                            
                            sum = sum + value 
                
                    else:         
                        
                        if meanTuples[i][0] != 'None' and meanTuples[i][0] != None :
                        
                            value = ( float(meanTuples[i][0]) ) 
                            
                            if  value > max:
                                max = value
                            if  value < min or min == None :
                                min = value 
                            
                            sum = sum + value 
                            
                        else:# don't count non-filled entries in mean.
                            nbEntries = nbEntries - 1
                            
                    
                if nbEntries != 0:            
                    avg = float(sum) / float(nbEntries)
                    
                total = float( sum ) * float( desiredInterval )
                  
        
        return min, max, avg, total
        
      
        
    def buildImageName( self, type, client, machine  ):
        """
            @summary : Builds and returns the image name to be created by rrdtool.
            
            @param type:
            
            @param client:
            
            @param machine:
            
            @param infos:
            
            @param logger:
            
            @return : Builds and returns the image name to be created by rrdtool.
        """
    
        _ = self.translatorForOutput
        
        span = self.timespan
        timeMeasure = _("hours")
        
        if self.timespan%(365*24) == 0 :
            span = int(self.timespan/(365*24))
            timeMeasure = _("years") 
        
        elif self.timespan%(30*24) == 0 :
            span = int(self.timespan/(30*24))
            timeMeasure = _("months") 
        
        elif self.timespan%24 == 0 :
            span = int(self.timespan/24)
            timeMeasure = _("days") 
           
                        
        date = self.endTime.replace( "-","" ).replace( " ", "_")
        
        translatedFileType = LanguageTools.translateTerm( self.fileType, self.inputLanguage, self.outputLanguage, CURRENT_MODULE_ABS_PATH )
        
        fileName = self.pathTowardsProducedGraphics.STATSGRAPHS + _( "others/rrd/%s/%s_%s_%s_%s_%s%s_on_%s.png" ) %( client, translatedFileType, client, date, type, span, timeMeasure, machine )
            
        fileName = fileName.replace( '[', '').replace(']', '').replace(" ", "").replace( "'","" )               
        
        splitName = fileName.split( "/" ) 
        
        if fileName[0] == "/":
            directory = "/"
        else:
            directory = ""
        
        for i in range( 1, len(splitName)-1 ):
            directory = directory + splitName[i] + "/"
        
            
        if not os.path.isdir( directory ):
            os.makedirs( directory, mode=0777 ) 
               
        return fileName 
    
    
            
    def formatMinMaxMeanTotal( self, minimum, maximum, mean, total, type, averageOrTotal = "average" ):
        """
            @summary : Formats min, max and median so that it can be used 
                        properly as a label on the produced graphic.
            
            @param minimum:
            
            @param maximum:
            
            @param mean:
            
            @param total:
            
            @param type:
            
            @param averageOrTotal:
            
            @return :The formated minimum, maximum, mean, total in a tuple of that order.
        """    
        
        _ = self.translatorForInput
        
        values = [ minimum, maximum, mean, total ]
        nbEntries = len(values)
        
        if type == _("bytecount") :
            
            for i in range( nbEntries ):
                
                if values[i] != None :
                    
                    if values[i] < 1000:#less than a k
                        if i != nbEntries-1:
                            values[i] = "%s B/Min" %int( values[i] )
                        else:
                            values[i] = "%s Bytes" %int( values[i] )
                    
                    elif values[i] < 1000000:#less than a meg 
                        if i != nbEntries-1:
                            values[i] = "%.2f KB/Min"  %( values[i]/1000.0 )
                        else:
                            values[i] = "%.2f kiloBytes" %( values[i]/1000.0 )
                    
                    elif values[i] < 1000000000:#less than a gig      
                        if i != nbEntries-1:
                            values[i] = "%.2f MB/Min"  %( values[i]/1000000.0 )
                        else:
                            values[i] = "%.2f MegaBytes" %( values[i]/1000000.0 )
                    
                    else:#larger than a gig
                        if i != nbEntries-1:
                            values[i] = "%.2f GB/Min"  %( values[i]/1000000000.0 )                 
                        else:
                            values[i] = "%.2f GigaBytes" %( values[i]/1000000000.0 )
            
        else:
        
            if type == _("filecount"):
                tag = _("Files")
            elif type == _("filesOverMaxLatency"):
                tag = _("F") 
            elif type == _("errors"):
                tag = _("Errors")
            elif type == _("latency"):
                tag = _("Avg")
                
            
            if minimum != None :
                if type == _("latency") or averageOrTotal == "average":
                    if minimum > 1:
                        minimum = "%.2f %s/Min" %( minimum, tag )
                    else: 
                        minimum = "%.4f %s/Min" %( minimum, tag )                
                
                else:
                    minimum = "%s" %int( minimum )
                       
            if maximum != None :
                if type == _("latency") or averageOrTotal == "average":    
                    if maximum > 1:
                        maximum = "%.2f %s/Min" %( maximum, tag ) 
                    else:    
                        maximum = "%.4f %s/Min" %( maximum, tag ) 
                else:
                    maximum = "%s" %int(maximum)
                    
            if mean != None :
                if mean > 1:
                    mean = "%.2f %s/Min" %( mean, tag )             
                else:    
                    mean = "%.4f %s/Min" %( mean, tag ) 
            
            if type == _("filesOverMaxLatency"):    
                tag = _("Files")
                
            total = "%s %s" %( int(total), tag )           
                        
            values = [ minimum, maximum, mean, total]
                
        return values[0], values[1], values[2], values[3]            
        
        
    
    def getGraphicsLegend( self,  maximum ):
        """
            @summary : Returns the legend according to the 
                       unit that is anticipated to be displayed within the graphics.
                       
            @param maximum :The legend is based on the maximum observed.
            
            @return : The graphics legend.
            
        """
        
        _ = self.translatorForOutput
        
        legend = ""
       
         
        if "KB" in str(maximum):
            legend = _("k on the y axis stands for kilo, meaning x thousands.")
        elif "MB" in str(maximum):
            legend = _("M on the y axis stands for Mega, meaning x millions.")
        elif "GB" in str(maximum):
            legend = _("G on the y axis stats for giga, meaning x billions.")
        else:
            
            try:
                maximum = float( str(maximum).split(" ")[0] )          
                
                if maximum > 1000000000:
                    legend = _("G on the y axis stats for giga, meaning x billions.")
                elif maximum > 1000000:
                    legend = _("M on the y axis stands for Mega, meaning x millions.")
                elif maximum > 1000:    
                    legend = _("k on the y axis stands for kilo, meaning x thousands.")
                elif maximum < .1000:
                    legend = _("m on the y axis stands for milli, meaning x thousandths.")
                   
            except:            
                pass
            
        return legend
               
       
                
    def getInterval( self, startTime, timeOfLastUpdate, goal = "fetchData"  ):    
        """         
            @summary : Returns the interval that was used 
                      for data consolidation. 
            
                      If graphicsType is weekly, monthly or yearly 
                      interval returned will always be the same as 
                      long timeOfLastUpdate- startTime is within 
                      it's the maximum lenggth of it's associated RRA. 
                        
                      Otherwise it is based on the distance between
                      starTTime being used and the time of the 
                      last update of the database.
                        
                      Method is very usefull when handling totals.    
            
            @param startTime:
            
            @param timeOfLastUpdate:
            
            @param graphicType:
            
            @param goal:
           
           @return : The calculated interval
           
        """ 
        
        _ = self.translatorForInput
        
        if self.graphicType == None:
            self.graphicType = _("daily")
            
        #432000 is 5 days in seconds
        #1209600 is 14 days in seconds
        #21024000 is 243 days in seconds    
            
        if self.graphicType == _("yearly") and  (timeOfLastUpdate - startTime ):
            interval = 1440
        elif self.graphicType == _("monthly") and (timeOfLastUpdate - startTime ) < (21024000):
            interval = 240
        elif self.graphicType == _("weekly")  and (timeOfLastUpdate - startTime ) < (1209600):
            interval = 60  
        elif self.graphicType == _("daily")  and (timeOfLastUpdate - startTime ) < (432000):
            if goal == "fetchData":
                interval = 1                     
            else :
                interval = 10           
        
        elif ( timeOfLastUpdate - startTime ) < (432000):#less than 5 days
            if goal == "fetchData":
                interval = 1                    
            else :
                interval = 10
                             
        elif ( timeOfLastUpdate - startTime ) < (1209600):#less than two week
            interval = 60
            
        elif (timeOfLastUpdate - startTime) < (21024000):
            interval = 240
             
        else:
            interval = 1440    
            
           
        return interval
    
    
    
    
         
    def getArchiveCopyDestination( self, type, client, machine ):
        """
           @summary : This method returns the absolute path to the copy 
                      to create based on the time of creation of the 
                      graphic and the span of the graphic.
           
           @note: Precondition : graphic type must be either weekly, monthly or yearly. 
           
           @param type:
           
           @param client:
           
           @param machine:
           
           @param infos:
        
           @return : The carchive copy destination. 
        
        """
        
        _ = self.translatorForInput
        
        startTimeInSeconds = StatsDateLib.getSecondsSinceEpoch( self.startTime )
        currentYear, currentMonth, currentDay = StatsDateLib.getYearMonthDayInStrfTime( startTimeInSeconds ) 
        currentWeek = time.strftime( "%W", time.gmtime( startTimeInSeconds ) )
        
           
        if self.graphicType == _("weekly"):
            endOfDestination =  "%s/%s/%s.png" %( currentYear, type, currentWeek )
        
        elif self.graphicType == _("monthly"):
            endOfDestination =  "%s/%s/%s.png" %( currentYear,type, currentMonth )
        
        elif self.graphicType == _("yearly"):
            endOfDestination =  "%s/%s.png" %( type, currentYear )
        
        elif self.graphicType == _("daily"):
            endOfDestination = "%s/%s/%s/%s.png" %( currentYear, currentMonth, type, currentDay )
            
        #destination = "%s/%s/%s/%s" %( StatsPaths.STATSGRAPHSARCHIVES, infos.graphicType, infos.fileType, label, infos.graphicType, endOfDestination )
        totalForMachine = _('totalForMachine')
        
        
        #change translator since we're dealing with output from now on...
        _  = self.translatorForOutput
        translatedGraphicType = LanguageTools.translateTerm(self.graphicType, self.inputLanguage, self.outputLanguage, CURRENT_MODULE_ABS_PATH ) 
        
        if self.totals == True:
            if self.mergerType == totalForMachine:
                destination ="%s%s/%s/%s/%s/%s"  %( self.pathTowardsProducedGraphics.STATSGRAPHSARCHIVES, translatedGraphicType , _("totals"), machine, self.fileType, endOfDestination  )
            else:
                
                destination =  "%s%s/%s/%s/%s" %( StatsPaths.STATSGRAPHSARCHIVES, translatedGraphicType, self.fileType, client, endOfDestination )   
        else:  
            destination = "%s%s/%s/%s/%s" %( StatsPaths.STATSGRAPHSARCHIVES, translatedGraphicType, self.fileType, client, endOfDestination )
        
        
        #print destination
        return destination    
        
             
        
    def createCopy( self, client, type, machine, imageName ):
    
        """
            @summary : Create a copy in the appropriate 
                       folder to the file named imageName.
            
            @param client:
            @param type:
            @param machine:
            @param imageName:
            @param infos:
            
        
            
        """ 
       
        src         = imageName
        destination = self.getArchiveCopyDestination( self, type, client, machine )
    
        if not os.path.isdir( os.path.dirname( destination ) ):
            os.makedirs( os.path.dirname( destination ), mode=0777 )                                                      
            dirname = os.path.dirname( destination )                                                  
            
            while( dirname != StatsPaths.STATSGRAPHSARCHIVES[:-1] ):#[:-1] removes the last / character 
                        
                try:
                    os.chmod( dirname, 0777 )
                except:
                    pass
                
                dirname = os.path.dirname(dirname)
        
        
        if os.path.isfile( destination ):
            os.remove( destination )  
           
        shutil.copy( src, destination ) 
        try:
            os.chmod(imageName, 0777)
        except:
            pass 
        
        
        
    def formatedTypesForLables( self, type ):
        """
            @summary : Takes the type of a graphic to be drawn
                        ( latency, filesOverMaxLatency...) and formats
                        it so that it can be used in the graphics labels.
                        ( y-axis label and title)       
            
            @note : Will not format an unknown type.
            
            @param type:latency,filesOverMaxLatency, bytecount,filecount or errors.
            
            @return : Returns the formated title and y axis label 
            
        """
        
        _ = self.translatorForInput
        
        formatedTitle  = type 
        formatedYLabel = type
        
        if type == _("latency"):
            _ = self.translatorForOutput
            formatedTitle = _("Averaged latency per minute")   
            formatedYLabel = _("Latency(seconds)")    
        elif type== _("filesOverMaxLatency"):
            _ = self.translatorForOutput
            formatedTitle  = _("Latencies over 15 seconds")   
            formatedYLabel = _("Files/Minute")
        elif type== _("bytecount"):
            _ = self.translatorForOutput
            formatedTitle = _("Bytes/Minute")     
            formatedYLabel = _("Bytes/Minute")    
        elif type== _("filecount"):
            _ = self.translatorForOutput
            formatedTitle = _("Files/Minute")     
            formatedYLabel = _("Files/Minute")   
        elif type== _("errors"):
            _ = self.translatorForOutput
            formatedTitle = _("Errors/Minute") 
            formatedYLabel = _("Errors/Minute")        
                
        return formatedTitle, formatedYLabel
        
    
        
    def translateDataType( self, type ):
        """
            @summary : Takes a type of the currently used language 
                       and returns the english version of that type.
            
            @param type : Type to be translated, written in the currently 
                          used language.
            
            @return : Returns the translated type.                         
                        
        """
        
        _ = self.translatorForInput
        
        knownTypes= { _("bytecount"):"bytecount", _("filecount"):"filecount", _("errors"):"errors", _("latency"):"latency", _("filesOverMaxLatency"):"filesOverMaxLatency"}
        
        translatedType = ""
        
        if type in knownTypes:  
            translatedType = knownTypes[type]
        else :
            translatedType = type      
        
        return translatedType
    
    
            
            
            
    def plotRRDGraph( self, databaseName, type, fileType, client, machine, infos ):
        """
            @summary : This method is used to produce a rrd graphic.
            
            @param databaseName:
            
            @param type:
            
            @param fileType:
            
            @param client:
            
            @param machine:
            
            @param infos:
            
            @param logger:
            
        """
        
        errorOccured = False
        
        imageName    = self.buildImageName( type, client, machine )        
        start        = int ( StatsDateLib.getSecondsSinceEpoch ( infos.startTime ) ) 
        end          = int ( StatsDateLib.getSecondsSinceEpoch ( infos.endTime ) )  
        formatedTitleType, formatedYLabelType = self.formatedTypesForLables( type )          
    
        lastUpdate = RrdUtilities.getDatabaseTimeOfUpdate( databaseName, fileType )        
                      
        fetchedInterval = self.getInterval( start, lastUpdate, goal = "fetchData"  )  
        desiredInterval = self.getInterval( start, lastUpdate, goal = "plotGraphic"  )
        interval        = desiredInterval     
        minimum, maximum, mean, total = self.getGraphicsMinMaxMeanTotal(  databaseName, start, end, fetchedInterval,desiredInterval, type = "average" )
        
        
        minimum, maximum, mean, total = self.formatMinMaxMeanTotal( minimum, maximum, mean, total, type )            
        graphicsLegeng         = self.getGraphicsLegend( maximum )      
        graphicsNote           = self.getGraphicsNote( interval, type  )        
            
        
        if graphicsNote == "" and graphicsLegeng == "":
            comment = ""
        else:
            comment = _("Note(s):")
            
                
        if type == _("latency") :
            innerColor = "cd5c5c"
            outerColor = "8b0000"
            total = ""
            
        elif type == _("filesOverMaxLatency"):
            innerColor = "cd5c5c"
            outerColor = "8b0000"
            total = _("Total: ") + str( total )                
            
        elif type == _("bytecount") or type == _("filecount") :
            innerColor = "019EFF"
            outerColor = "080166"#"4D9AA9"  
            total = _("Total: ") + str(total)
            
        else:
            innerColor = "54DE4F"
            outerColor = "1C4A1A"     
            total = _("Total: ") + str(total)
            
        title = self.buildTitle( formatedTitleType, client, minimum, maximum, mean )   
              
        #note : in CDEF:realValue the i value can be changed from 1 to value of the interval variable
        #       in order to get the total displayed instead of the mean.
        
        translatedType = self.translateDataType(type)
        
        if infos.graphicType != _("monthly"):
            try:
                rrdtool.graph( imageName,'--imgformat', 'PNG','--width', '800','--height', '200','--start', "%i" %(start) ,'--end', "%s" %(end),'--step','%s' %(interval*60), '--vertical-label', '%s' %formatedYLabelType,'--title', '%s'%title, '--lower-limit','0','DEF:%s=%s:%s:AVERAGE'%( translatedType, databaseName, translatedType), 'CDEF:realValue=%s,%i,*' %( translatedType, 1), 'AREA:realValue#%s:%s' %( innerColor, translatedType ),'LINE1:realValue#%s:%s'%( outerColor, translatedType ), "COMMENT: " + _("Min: ") + str(minimum) + "   " + _("Max: ") + str(maximum) + "   " + _( "Mean: " ) + str(mean) + "   " +  str(total) + "\c", 'COMMENT:%s %s %s\c' %( comment, graphicsNote, graphicsLegeng )  )
            except Exception, inst:
                errorOccured = True
                #print _("Error : Could not generate ") + str(imageName)
                #print _("Error was : ") + str(inst)
        else:#With monthly graphics, we force the use the day of month number as the x label.       
            try:
                rrdtool.graph( imageName,'--imgformat', 'PNG','--width', '800','--height', '200','--start', "%i" %(start) ,'--end', "%s" %(end),'--step','%s' %(interval*60), '--vertical-label', '%s' %formatedYLabelType,'--title', '%s'%title, '--lower-limit','0','DEF:%s=%s:%s:AVERAGE'%( translatedType, databaseName, translatedType), 'CDEF:realValue=%s,%i,*' %( translatedType, 1), 'AREA:realValue#%s:%s' %( innerColor, translatedType ),'LINE1:realValue#%s:%s'%( outerColor, translatedType ), '--x-grid', 'HOUR:24:DAY:1:DAY:1:0:%d',"COMMENT: " + _("Min: ") + str(minimum) + "   " + _("Max: ") + str(maximum) + "   " + _( "Mean: " ) + str(mean) + "   " +  str(total) + "\c", 'COMMENT:%s %s %s\c' %(comment,graphicsNote, graphicsLegeng)  )    
            except Exception, inst:
                errorOccured = True
                #print _("Error : Could not generate ") + str( imageName )
                #print _("Error was : ") + str(inst)
                
        if errorOccured == False:
            try:
                os.chmod(imageName, 0777)
            except:
                pass
            
            if infos.copy == True:
                self.createCopy( client, type, machine, imageName )
            
            if self.logger != None:
                try:
                    self.logger.info(  _("Plotted : ") + str(imageName) )
                except:
                    pass    
        else:
            
            if self.logger != None:
                try:
                    self.logger.error(  _("Error : Could not generate ") + str( imageName ) )     
                except:
                    pass    
                
        return  imageName           
    
    
    
    def createNewMergedDatabase( self, dataType,  machine, start, interval    ) :       
        """
        
        @summary: Creates a brand new database for data merging based on parameters.
            
            
            
        
        @note:  If a database with the same name allready exists, it will be removed.
                
                Databases are created with rras that are identical to those found in the 
                transferPickleToRRD.py file. If databases are to change there they must be
                changed here also.  
        
        
        @param dataType: errors, bytecount,filecount, latency or filesOverMaxLatency
        
        @param machine: machine from wich the data comes from. If data comes form two machines, 
                        group the names togehter EX : machine1 and machine2 become machine1machine1
        
        @param infos: _GraphicsInfos instance that is used throughout the program.
        
        """    
                                                      
        rrdFilename = RrdUtilities.buildRRDFileName( dataType = dataType, clients = self.clientNames, machines =[machine], fileType = self.fileType, usage =self.mergerType)
           
        
        if interval == 1:#daily :
            #print "daily 240 "
            start = start - 60
            #print "^^^^^^^^^^^", rrdFilename, '--start','%s' %( start ), '--step', '60', 'DS:%s:GAUGE:60:U:U' %dataType,'RRA:AVERAGE:0:1:7200','RRA:MIN:0:1:7200', 'RRA:MAX:0:1:7200'
            rrdtool.create( rrdFilename, '--start','%s' %( start ), '--step', '60', 'DS:%s:GAUGE:60:U:U' %self.translateDataType( dataType ),'RRA:AVERAGE:0:1:7200','RRA:MIN:0:1:7200', 'RRA:MAX:0:1:7200' )
        
        
        elif interval == 60:#weekly :
            start = start - (60*60)
            rrdtool.create( rrdFilename, '--start','%s' %( start ), '--step', '3600', 'DS:%s:GAUGE:3600:U:U' %self.translateDataType( dataType ),'RRA:AVERAGE:0:1:336','RRA:MIN:0:1:336', 'RRA:MAX:0:1:336' )
            #print "weekly 240 "
        
        elif interval == 240:#monthly
            #print "monthly 240 "
            start = start - (240*60)
            rrdtool.create( rrdFilename, '--start','%s' %( start ), '--step', '14400', 'DS:%s:GAUGE:14400:U:U' %self.translateDataType( dataType ), 'RRA:AVERAGE:0:1:1460','RRA:MIN:0:1:1460','RRA:MAX:0:1:1460' )
        
        
        else:#yearly
            #print "yearly 1440 "
            start = start - (1440*60)
            rrdtool.create( rrdFilename, '--start','%s' %( start ), '--step', '86400', 'DS:%s:GAUGE:86400:U:U' %self.translateDataType( dataType ), 'RRA:AVERAGE:0:1:3650','RRA:MIN:0:1:3650','RRA:MAX:0:1:3650' )
        
        try:
            os.chmod( rrdFilename, 0777 )
        except:
            pass    
        
        return rrdFilename
        

    
    def getNormalisedDataBaseData( data, desiredNumberOfEntries, mergerType = "average" ):
        """
            @summary : This methods takes an array of x entries 
                       and tranforms it into an array of y entries.
            
            @note: If desiredNumberOfEntries is bigger then the number 
                   of entries within the data or if the length of data 
                   % desiredNumberOfEntries is not equal to 0 the original 
                   data will be returned un modified.
            
            @param data: Array containing the data we need to normalise.
            
            @param desiredNumberOfEntries: The number of entries to wich 
                                           the array needs to be reduced.
                                           
            @param mergerType : Wheter to merge the data per average or by total.
                                           
            @return: Returns the normalised array.                                       
            
        
        """
        
        newArray = []
        
        if ( len(data) > desiredNumberOfEntries ) and (len(data) % desiredNumberOfEntries == 0 ) :
        
            nbOldEntriesPerNewEntry = len(data) / desiredNumberOfEntries 
            newValue = 0
            
            for i in range(len(data)):
                if i != 0 and (i%nbOldEntriesPerNewEntry) ==0:
                    if mergerType == "average" :
                        newArray.append( float(newValue)/float(nbOldEntriesPerNewEntry) ) 
                    else:
                        newArray.append( float(newValue) )    
    
                    newValue =0
                    
                newValue = newValue + data[i]    
            
            if mergerType == "average" :
                newArray.append( float(newValue)/float(nbOldEntriesPerNewEntry) ) 
            else:
                newArray.append( float(newValue) ) 
            
        else:
            newArray = data 
            
        return newArray        
    
    getNormalisedDataBaseData = staticmethod( getNormalisedDataBaseData )
    
    
    
    def getDesirableArrayLength( arrays ):
        """
            @summary : Receives a series of arrays and returns 
                       the most popular length amongst the arrays.
            
            @param arrays : List of arrays to analyse.
            
            @return : The most popular array size.              
                       
        """
        
        maximumPopularity = 0
        mostPopular = 0
        arraySizes = {}
        
        
        for array in arrays:
            arraySize = len(array)
            
            if arraySize in arraySizes:
                arraySizes[arraySize] = arraySizes[arraySize] + 1 
            else:
                arraySizes[arraySize] = 1     
        
        for arraySize in arraySizes:
            if arraySizes[arraySize] > maximumPopularity:
                mostPopular = arraySize
                maximumPopularity = arraySizes[arraySize]
                 
        return mostPopular    
        
    getDesirableArrayLength = staticmethod( getDesirableArrayLength )
    
    
    
    def getDataForAllSourlients( self, dataType = "fileCount" ):
        """ 
            @summary : 
            
            @param infos: Infos with whom the program the program what was. 
            
            @return : Returns the dictionary containing the timespant filecount 
                      associations for all sourlients.
            
        """
        
        
        data = {} 
        
        # Get filecount value for each sourlient.
        for client in self.clientNames:#Gather all pairs for that type
            
            databaseName = RrdUtilities.buildRRDFileName( dataType = dataType, clients = [client], machines = self.machines, fileType = self.fileType) 
            if not os.path.isfile(databaseName):
                databaseName = RrdUtilities.buildRRDFileName( dataType = dataType, groupName =  client, machines = self.machines, fileType = self.fileType, usage = "group" ) 
            
            #print databaseName
            if self.totals == True :#try and force all databases to give back data with the exact same resolution.
                
                timeOfLastUpdate = RrdUtilities.getDatabaseTimeOfUpdate(databaseName, "tx")
                interval = self.getInterval( StatsDateLib.getSecondsSinceEpoch(self.startTime), timeOfLastUpdate,  "fetchData" )
                resolution = int(interval*60)
                output = commands.getoutput( "rrdtool fetch %s  'AVERAGE' -r '%s' -s %s  -e %s" %(  databaseName, str(resolution), int(StatsDateLib.getSecondsSinceEpoch(self.startTime)), int(StatsDateLib.getSecondsSinceEpoch(self.endTime) ) ) )
                
            else:    
                output = commands.getoutput("rrdtool fetch %s  'AVERAGE' -s %s  -e %s" %( databaseName, int(StatsDateLib.getSecondsSinceEpoch(self.startTime)), int(StatsDateLib.getSecondsSinceEpoch(self.endTime) ) ))
                
            #print output 
            clientsData = []
            splitOutputLines = []
            splitOutputLines = output.splitlines()[2:]
            
            for line in splitOutputLines:
                try:
                    value = float(line.split(":")[1].replace(" ","") ) 
                except: 
                    value = 0.0    
                clientsData.append(value )
            
            data[client] = clientsData[:-1]
        
        
        return data     
    


    def getDatabaseNames( self, datatype ):
        """
            @summary : Returns the database names associated with 
                       the received parameters.  
        
           
            @param datatype : Type of data were are interested in
                              (latency, filecount,bytecount,error,)

            
            @return:  Returns the list of database names found in 
                      a dictionary format with {sourlient:databaseName }
                      associations.
            
        """
        
        databaseNames = {}
        
        for sourlient in self.clientNames:
            databaseName = RrdUtilities.buildRRDFileName( dataType = datatype , clients = sourlient, machines = self.machines, fileType = self.fileType ) 
            if not os.path.isfile(databaseName):
                databaseName = RrdUtilities.buildRRDFileName( dataType = datatype , groupName = sourlient, machines = self.machines, fileType = self.fileType, usage="group" ) 
            if not os.path.isfile(databaseName):
                databaseName = ""
                
            databaseNames[sourlient] = databaseName
        
        return databaseNames
    
    
    
    def getTimeStamps( self, start, end, dataType ):
        """
            @summary : builds the series of different time 
                       stamps that are found between start 
                       and end based on the span type.  
            
            @param start : startTime of the span we are interested in.
            
            @param end   : endTime of the span we are interested in.
            
            @param dataType : Datatype we are currently working with( latency, filecount,bytecount,error,)
        
            @return   : Returns the list of timestamps.
             
             
        """
        
        timeStamps = []
        
        databaseNames = self.getDatabaseNames( self.clientNames, self.fileType, dataType, self.machines )
        timeOfLastUpdate = RrdUtilities.getMostPopularTimeOfLastUpdate(databaseNames) 
        interval = self.getInterval( start, timeOfLastUpdate, "fetchData")
        interval = interval * 60
        
        timeStamp = start
        while timeStamp < end :
            timeStamps.append( timeStamp )
            timeStamp = timeStamp + interval
        #print timeStamps
        
        return timeStamps 
        
        
        
    def getFileCountsTotals( fileCounts ):
        """    
            @summary : Takes filecounts dictionary containing an entry 
                       for all sourlients for every time stamps. 
                      
            @note : All arraysd must be of the same length          
                       
            @param fileCounts: Array containing dictionaries with 
                              {sourlient:value} associations.             
            
            @return: Returns an array containing the total of files
                     for every time stamp 
            
            
        """
        
        fileCountsTotals = []
        valueToAdd = 0 
        
        nbEntries = len( fileCounts[fileCounts.keys()[0]] )
         
        for i in range(nbEntries) : 
            valueToAdd = 0.0
            
            for sourlient in fileCounts.keys() :
                fileCountToAdd = fileCounts[sourlient][i]
                if str(fileCountToAdd) != 'nan':
                    valueToAdd = valueToAdd + fileCountToAdd
                
            fileCountsTotals.append( valueToAdd )
            
                
        return fileCountsTotals
        
    getFileCountsTotals = staticmethod(getFileCountsTotals)
        
    
        
    def mergeData( timeStamps, fileCounts, data, withProportions = False, mergerTypeWithoutProportions = "average" ):
        """
    
            @summary : Takes an array containing data values 
                       for every time stamps received in parameter and 
                       combines the data for every time stamps following 
                       the fileCounts proportions  
           
            @param timeStamps: Array containing the timestamps to be 
                                used when plotting the graphics. 
            
            @param fileCounts: Array containing the file counts values for 
                               every sourlient for every time stamps.ex [{'bob':123}]
            
            @param data:  Array containing the values of a specific data type for 
                          every sourlient for every time stamps.ex [{'bob':123}]
            
            @param withProportions: Whether or not to use filecount poportions
                                    when merging the data. When set to True,
                                    every value will be multiplied by the ratio of 
                                    files the currently handled sourlient has
                                    sent or received in proportion with the 
                                    total sent or received during that time
                                    stamp.     
                                    
                                        
            @param mergerTypeWithoutProportions: Specifies whether to use 'average' or 'total'
                                                 when merging without proportions. 
                                                  
            
            @return: Returns the merged data in the following form :
                    [(timestamp1,value1),(timestamp2,value2)]
                                 
        
        """
        
        i=0
        mergedData = []
        valueToAdd = 0.0
        
        if withProportions == True:
            fileCountsTotals = RRDGraphicProducer.getFileCountsTotals(fileCounts)
        
        for i in range( len(timeStamps) ):
            valueToAdd = 0.0
            
            for sourlient in data.keys():
                sourlientsValue = data[sourlient][i]
                #print "%s %s : %s" %(timeStamps[i], sourlient, sourlientsValue)
                if ( str(sourlientsValue) != 'nan'):
                    if withProportions == True:
                        #print float(sourlientsValue), float( float(fileCounts[sourlient][i])), float(fileCountsTotals[i])
                        if float(fileCountsTotals[i]) !=0.0:
                            valueToAdd = valueToAdd + float(sourlientsValue) * float( float(fileCounts[sourlient][i]) / float(fileCountsTotals[i]) )
                    else:
                        valueToAdd = valueToAdd + float(sourlientsValue)
                        
            if withProportions == False:
                if mergerTypeWithoutProportions == "average":
                    valueToAdd = float(valueToAdd) / float( len( data.keys() ) ) 
                    #print "did the avrage"     
            
            mergedData.append( [timeStamps[i], valueToAdd] )
        
        #print mergedData
        return mergedData
        
    mergeData = staticmethod(mergeData)    
        
        
        
    def getPairsFromDatabases( self, type, machine, start, end, \
                               mergeWithProportions = False, 
                               mergerTypeWithoutProportions = "average" ):
        """
        
            @summary : Takes the data pairs from the wanted 
                       client/sources of a machine, 
                       merges all it's data into a series of 
                       pairs and returns those pairs. 
                       
                       When using this method, data will be merged 
                       together in proportion with the "weight" of 
                       each client/sources. Meaning that a 
                       client/source that is handling   
            
            @param type : Data type : latency, bytecount, filecount etc.
            
            @param start : Start of the span of data we are interested in.
            
            @param end : End of the span of data we are interested in.
            
            @param mergeWithProportions : Whether or not to merge the data based
                                          on the filecount ratio of each sourlients
                                          or not.
                                           
            @param logger : Logger in wich to write log entries. 
            
            @return :  The merged data pairs.     
        
        """
        
        fileCounts = {}
    
        timeStamps = self.getTimeStamps(start, end, type)
        
        data = self.getDataForAllSourlients(  type  )
        
        desirableArrayLength = len(timeStamps)
        
        if desirableArrayLength != len(timeStamps):
            #print timeStamps
            raise Exception("desirableArrayLength(%s) != len(timeStamps)(%s)" %(desirableArrayLength, len(timeStamps) ) )
        
        for sourlient in data.keys() :
            if len( data[sourlient]) != desirableArrayLength:
                #print "len before %s %s" %(len( data[sourlient]), desirableArrayLength )
                
                #--------------------------------- if mergeWithProportions == True :
                    #---------------------------------------- mergerType = "average"
                #------------------------------------------------------------ else :
                    #--------------------- mergerType = mergerTypeWithoutProportions
                data[sourlient] = self.getNormalisedDataBaseData(data[sourlient], desirableArrayLength, mergerType="average" )   
                #print "len after %s" %len(data[sourlient])
        
        if mergeWithProportions == True :
            
            fileCounts = self.getDataForAllSourlients( _("filecount") )
            
            for sourlient in fileCounts.keys():
                if len( fileCounts[sourlient]) != desirableArrayLength:
                    fileCounts[sourlient] = self.getNormalisedDataBaseData(fileCounts[sourlient], desirableArrayLength, mergerType="average")  
                    if len( fileCounts[sourlient]) != desirableArrayLength:
                        if self.logger != None :
                            self.logger.error(  _("%s still has a problem %s %s ") %(sourlient, len( fileCounts[sourlient]), desirableArrayLength ) )
                        #print  
                    
                    
            pairs = RRDGraphicProducer.mergeData(timeStamps, fileCounts, data, withProportions = True)
        
        else:
            pairs = RRDGraphicProducer.mergeData(timeStamps, fileCounts, data, withProportions = False, mergerTypeWithoutProportions = mergerTypeWithoutProportions)
                
                
        return pairs
    
    
    
        
    def getPairsFromAllDatabases( self, type, machine, start, end ):
        """
            @summary : This method gathers all the needed data between start and end 
                       from all the databases wich are of the specifed type and
                       from the specified machine and that rekate to the specified 
                       client/sources.
            
            @param type : Data type : latency, bytecount, filecount etc.
            
            @param start : Start of the span of data we are interested in.
            
            @param end : End of the span of data we are interested in.
            
            @param infos : _GraphicsInfos instance containing vital infos.
            
            @param logger : Logger in wich to write log entries. 
            
            @return : Array containing one tuple entry per timestamp of the following form : 
                     ( timestamp, combinedValue ) pairs.
            
        """
        
        pairs = []
        
        if type == _("latency"):
            pairs = self.getPairsFromDatabases( type, machine, start, end,  mergeWithProportions = True ) 
            #pairs = getPairsFromDatabasesWithoutProportions( type, machine, start, end, infos, logger=None )       
        else :
            pairs = self.getPairsFromDatabases( type, machine, start, end, mergeWithProportions = False, mergerTypeWithoutProportions = "total" )
            
        return pairs        
        
        
        
        
        
    def createMergedDatabases( self ):
        """
            Gathers data from all needed databases.
            
            Creates new databases to hold merged data.
            
            Feeds new databases with merged data. 
            
            Returns the list of created databases names.
             
        """            
        
        i = 0
        lastUpdate = 0
        typeData   = {}
        start      = int( StatsDateLib.getSecondsSinceEpoch ( self.startTime )  )
        end        = int( StatsDateLib.getSecondsSinceEpoch ( self.endTime )    ) 
        databaseNames = {}
        
    
        for machine in self.machines:
            
            for type in self.types :       
                            
                typeData[type] = {}
                i = 0 
                while i < len(self.clientNames) and lastUpdate == 0 :
                    databaseName = RrdUtilities.buildRRDFileName( dataType = type, clients = [self.clientNames[i]] , machines = [machine],  fileType = self.fileType, usage = "regular"  )
                    if not os.path.isfile(databaseName):
                        RrdUtilities.buildRRDFileName( dataType = type, groupName = self.clientNames[i] , machines = [machine],  fileType = self.fileType, usage = "group"  )    
                    
                    lastUpdate  =  RrdUtilities.getDatabaseTimeOfUpdate( databaseName, self.fileType )
                
                interval = self.getInterval( start, lastUpdate, goal = "fetchData"  )    
                
                pairs = self.getPairsFromAllDatabases( type, machine, start, end )                        
                   
                combinedDatabaseName = self.createNewMergedDatabase( dataType = type, machine = machine, interval = interval,start = start   )
                                                         
                databaseNames[type] = combinedDatabaseName                            
                    
                for pair in pairs:
                    if pair[1] != None :
                        rrdtool.update( combinedDatabaseName, '%s:%s' %( int(pair[0]), pair[1] ) )
                        
                try:            
                    RrdUtilities.setDatabaseTimeOfUpdate(combinedDatabaseName, self.fileType, lastUpdate)
                except:
                    pass
                    
        return databaseNames
                        
                
                
    def generateRRDGraphics( self, verbose = False ):
        """
            @summary : This method generates all the graphics. 
                    
        """    
            
        plottedGraphics = []
            
        if self.totals: #Graphics based on total values from a group of clients.
            #todo : Make 2 title options
            
            databaseNames = self.createMergedDatabases()
            
            clientName = ''
            for client in self.clientNames:    
                clientName = clientName +  client
                   
            for machine in self.machines:#in total graphics there should be only one iteration...
                for type in self.types:
                    if self.mergerType == 'regular':
                        plottedGraphics.append( self.plotRRDGraph( databaseNames[type], type, clientName, machine ) )
                    else:
                        plottedGraphics.append(self.plotRRDGraph( databaseNames[type], type, self.fileType, machine ) )
                  
        else:
            
            for machine in self.machines:
                
                for client in self.clientNames:
                    
                    for type in self.types : 
                       
                        databaseName = RrdUtilities.buildRRDFileName( dataType = type, clients = [client], machines = [machine], fileType = self.fileType )
                        if not os.path.isfile(databaseName):
                            databaseName = RrdUtilities.buildRRDFileName( dataType = type, groupName=client, machines = [machine], fileType = self.fileType, usage = "group" )
                        
                        plottedGraphics.append( self.plotRRDGraph( databaseName, type, client, machine )        )
            
            
        return plottedGraphics   
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
        