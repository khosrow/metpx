#!/usr/bin/env python2
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: Plotter.py
#
# Author      : Nicholas Lemay, but the code is highly inspired by previously created file 
#               named Plotter.py written by Daniel Lemay. This file can be found in the lib
#               folder of this application. 
#
# Date        : 2006-06-06
#
# Description : This class contain the data structure and the methods used to plot a graphic 
#               using previously collected data. The data should have been collected using 
#               the data collecting class' and methods found in the stats library. 
# 
#############################################################################################
"""


#important files 
import sys 
import MyDateLib
from MyDateLib import *
import ClientStatsPickler
from Numeric import *
import Gnuplot, Gnuplot.funcutils
import copy 
import PXPaths
import logging 
from   Logger  import *

PXPaths.normalPaths()

localMachine = os.uname()[1]


class StatsPlotter:

    def __init__( self, timespan,  stats = None, clientNames = None, type='impulses', interval=1, imageName="gnuplotOutput", title = "Stats",currentTime = "",now = False, statsTypes = None, productType = "All", logger = None, fileType = "tx", machines = "", entryType = "minute", maxLatency = 15 ):
        """
            StatsPlotter constructor. 
            
        """
        
        x = [ [0]*5  for x in range(5) ]
        
        for i in range( len(machines) ):
            if machines[i] == "pds3-dev":
                machines[i] = "pds5"
            elif machines[i] == "pds4-dev":
                machines[i] = "pds6"
        
        print machines    
        machines = "%s" %machines
        machines = machines.replace( "[","").replace( "]","" ).replace( "'", "" )
        
        self.now         = now                     # False means we round to the top of the hour, True we don't
        self.stats       = stats or []             # ClientStatsPickler instance.
        self.clientNames = clientNames or []       # Clients for wich we are producing the graphics. 
        self.timespan    = timespan                # Helpfull to build titles 
        self.currentTime = currentTime             # Time of call
        self.type        = type                    # Must be in: ['linespoint', 'lines', 'boxes', 'impulses'].
        self.fileType    = fileType                # Type of file for wich the data was collected
        self.imageName   = imageName               # Name of the image file.
        self.nbFiles     = []                      # Number of files found in the data collected per server.
        self.nbErrors    = []                      # Number of errors found per server
        self.graph       = Gnuplot.Gnuplot()       # The gnuplot graphic object itself. 
        self.timeOfMax   = [[]]                    # Time where the maximum value occured.  
        self.machines    = machines                # List of machine where we collected info.
        self.entryType   = entryType               # Entry type :  minute, hour, week, month
        self.clientName  = ""                      # Name of the client we are dealing with 
        self.maxLatency  = maxLatency              # Maximum latency 
        self.maximums    = [[]]                    # List of all maximum values 1 for each graphic.
        self.minimums    = [[]]                    # Minimum value of all pairs.
        self.means       = [[]]                    # Mean of all the pairs.
        self.maxFileNames= [[]]                    # Name of file where value is the highest .
        self.filesWhereMaxOccured = [[]]           # List of files for wich said maximums occured.  
        self.statsTypes  = statsTypes or []        # List of data types to plot per client.
        self.nbFilesOverMaxLatency = []            # Numbers of files for wich the latency was too long.
        self.ratioOverLatency      = []            # % of files for wich the latency was too long. 
        self.const = len( self.stats ) -1          # Usefull constant
        self.productType = productType             # Type of product for wich the graph is being generated.  
        self.initialiseArrays()
        self.loggerName       = 'statsPlotter'
        self.logger           = logger
        
        
        if self.logger == None: # Enable logging
            if not os.path.isdir( PXPaths.LOG + localMachine + '/' ):
                os.makedirs( PXPaths.LOG + localMachine + '/', mode=0777 )
            self.logger = Logger( PXPaths.LOG + localMachine + '/' + 'stats_' + self.loggerName + '.log', 'INFO', 'TX' + self.loggerName, bytes = True  ) 
            self.logger = self.logger.getLogger()
            
        self.xtics       = self.getXTics( )        # Seperators on the x axis.
    
    
    def initialiseArrays( self ):
        """
            Used to set the size of the numerous arrays needed in StatsPlotter
        """
        
        nbClients = len( self.clientNames )
        nbTypes   = len( self.statsTypes )
        
        self.nbFiles = [0] * nbClients
        self.nbErrors = [0] * nbClients
        self.nbFilesOverMaxLatency = [0] * nbClients
        self.ratioOverLatency      = [0.0] * nbClients
        self.timeOfMax   = [ [0]*nbTypes  for x in range( nbClients ) ]
        self.maximums    = [ [0.0]*nbTypes  for x in range( nbClients ) ] 
        self.minimums    = [ [0.0]*nbTypes  for x in range( nbClients ) ]
        self.means       = [ [0.0]*nbTypes  for x in range( nbClients ) ]
        self.maxFileNames= [ [0.0]*nbTypes  for x in range( nbClients ) ]
        self.filesWhereMaxOccured =  [ [0.0]*nbTypes  for x in range( nbClients ) ] 
            
        
    def buildImageName( self ):
        """
            Builds and returns the absolute fileName so that it can be saved 
            
            If folder to file does not exists creates it.
        
        """ 
        
        clientName = ""
        
        if len( self.clientNames ) == 0:
            clientName = self.clientNames[0]
        else:
            for name in self.clientNames :
                clientName = clientName + name  
                if name != self.clientNames[ len(self.clientNames) -1 ] :
                    clientName = clientName + "-"  
        
        date = self.currentTime.replace( "-","" ).replace( " ", "_")
        
        fileName = PXPaths.GRAPHS + "%s/%s_%s_%s_%s_%shours_on_%s.png" %( clientName, self.fileType, clientName, date, self.statsTypes, self.timespan, self.machines )
        
        
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
    
    
        
    def getXTics( self ):
        """
           
           This method builds all the xtics used to seperate data on the x axis.
            
           Xtics values will are used in the plot method so they will be drawn on 
           the graphic. 
           
           Note : All xtics will be devided hourly. This means a new xtic everytime 
                  another hour has passed since the starting point.  
            
            
        """
        #print "get x tics"
        if self.logger != None :
            self.logger.debug( "Call to getXtics received" )
        
        nbBuckets = ( len( self.stats[0].statsCollection.timeSeperators ) )
        xtics = ''
        startTime = MyDateLib.getSecondsSinceEpoch( self.stats[0].statsCollection.timeSeperators[0] )
        
        if nbBuckets != 0 :
            
            for i in range(0, nbBuckets ):
                 
                   
                if ( (  MyDateLib.getSecondsSinceEpoch(self.stats[0].statsCollection.timeSeperators[i]) - ( startTime  ) ) %(60*60)  == 0.0 ): 
                    
                    hour = MyDateLib.getHoursFromIso( self.stats[0].statsCollection.timeSeperators[i] )
                    
                    xtics += '"%s" %i, '%(  hour , MyDateLib.getSecondsSinceEpoch(self.stats[0].statsCollection.timeSeperators[i] ) )

        
        
        return xtics[:-2]
         
        
        
    def getPairs( self, clientCount , statType, typeCount  ):
        """
           
           This method is used to create the data couples used to draw the graphic.
           Couples are a combination of the data previously gathered and the time
           at wich data was produced.  
           
           Note : One point per pair will generally be drawn on the graphic but
                  certain graph types might combine a few pairs before drawing only 
                  one point for the entire combination.
                  
           Warning : If illegal statype is found program will be terminated here.       
        
        """
        
        if self.logger != None: 
            self.logger.debug( "Call to getPairs received." )
        
        k = 0 
        pairs = []
        total = 0
        self.nbFiles[clientCount]  = 0
        self.nbErrors[clientCount] = 0
        self.nbFilesOverMaxLatency[clientCount] = 0
        nbEntries = len( self.stats[clientCount].statsCollection.timeSeperators )-1 
               
        
        if nbEntries !=0:
            
            total = 0
                            
            self.minimums[clientCount][typeCount] = 100000000000000000000 #huge integer
            self.maximums[clientCount][typeCount] = None
            self.filesWhereMaxOccured[clientCount][typeCount] =  "" 
            self.timeOfMax[clientCount][typeCount] = ""
            
            for k in range( 0, nbEntries ):
                
                try :
                    
                    if len( self.stats[clientCount].statsCollection.fileEntries[k].means ) >=1 :
                                                
                        if statType == "latency":
                            self.nbFilesOverMaxLatency[clientCount] = self.nbFilesOverMaxLatency[ clientCount ] + self.stats[clientCount].statsCollection.fileEntries[k].filesOverMaxLatency    
                    
                        if statType == "errors":
                            
                            pairs.append( [MyDateLib.getSecondsSinceEpoch(self.stats[clientCount].statsCollection.timeSeperators[k]), self.stats[clientCount].statsCollection.fileEntries[k].totals[statType]] )
                        
                            #calculate total number of errors
                            self.nbErrors[clientCount] = self.nbErrors[clientCount] + self.stats[clientCount].statsCollection.fileEntries[k].totals[statType] 
                            
                            
                        else:
                            
                            pairs.append( [ MyDateLib.getSecondsSinceEpoch(self.stats[clientCount].statsCollection.timeSeperators[k]), self.stats[clientCount].statsCollection.fileEntries[k].totals[statType]] )
                            
                        
                        if( self.stats[clientCount].statsCollection.fileEntries[k].maximums[statType]  > self.maximums[clientCount][typeCount] ) :
                            
                            self.maximums[clientCount][typeCount] =  self.stats[clientCount].statsCollection.fileEntries[k].maximums[statType]
                            
                            self.timeOfMax[clientCount][typeCount] = self.stats[clientCount].statsCollection.fileEntries[k].timesWhereMaxOccured[statType]
                            
                            self.filesWhereMaxOccured[clientCount][typeCount] = self.stats[clientCount].statsCollection.fileEntries[k].filesWhereMaxOccured[statType]
                        
                            
                        elif self.stats[clientCount].statsCollection.fileEntries[k].minimums[statType] < self.minimums[clientCount][typeCount] :      
                            
                            if not ( statType == "bytecount" and  self.stats[clientCount].statsCollection.fileEntries[k].minimums[statType] == 0 ):
                                self.minimums[clientCount][typeCount] = pairs[k][1]
                                                    
                        self.nbFiles[clientCount]  = self.nbFiles[clientCount]  + self.stats[clientCount].statsCollection.fileEntries[k].nbFiles   
                   
                              
                    else:
                   
                        pairs.append( [ MyDateLib.getSecondsSinceEpoch(self.stats[clientCount].statsCollection.timeSeperators[k]), 0.0 ] )
                
                
                except KeyError:
                    
                    self.logger.error( "Error in getPairs." )
                    self.logger.error( "The %s stat type was not found in previously collected data." %statType )    
                    pairs.append( [ MyDateLib.getSecondsSinceEpoch(self.stats[clientCount].statsCollection.timeSeperators[k]), 0.0 ] )
                    pass    
                
                
                total = total + pairs[k][1]            
            
            self.means[clientCount][typeCount] = (total / (k+1) ) 
            
            
            if self.nbFiles[clientCount] != 0 :
                self.ratioOverLatency[clientCount]  = float( float(self.nbFilesOverMaxLatency[clientCount]) / float(self.nbFiles[clientCount]) ) *100.0
            
            if self.minimums[clientCount][typeCount] == 100000000000000000000 :
                self.minimums[clientCount][typeCount] = None
                   
            return pairs    



    def getMaxPairValue( self, pairs ):
        """
            Returns the maximum value of a list of pairs. 
        
        """
        
        maximum = 0 
        
        if len( pairs) != 0 :
            
            for pair in pairs:
                if pair[1] > maximum:    
                    maximum = pair[1] 
                    
                    
        return  maximum 
        
        
                    
    def buildTitle( self, i, statType, typeCount ):
        """
            This method is used to build the title we'll print on the graphic.
            Title is built with the current time and the name of the client where
            we collected the data. Also contains the mean and absolute min and max found 
            in the data used to build the graphic.          
               
        """  
        
        if self.maximums[i][typeCount] !=None :
            maximum =("%3.2f") %self.maximums[i][typeCount]
        
        else:
            maximum = None
                 
        if self.minimums[i][typeCount] != None :
            minimum = ("%3.2f") %self.minimums[i][typeCount]
        else:
            minimum = None
        
              
        title =  "%s for %s queried at %s for a span of %s hours \\n\\nMAX: %s,  MEAN: %3.2f, MIN: %s " %( statType, self.clientNames[i],  self.currentTime , self.timespan,  maximum, self.means[i][typeCount], minimum )     
        
        return title
        
    
    def createLink( self ):
        """
            Creates a symbolic link between created image file and 
            an shorter, easier to read name. 
            
        """
        clientName = ""
        
        if len( self.clientNames ) == 0:
            clientName = self.clientNames[0]
        else:
            for name in self.clientNames :
                clientName = clientName + name  
                if name != self.clientNames[ len(self.clientNames) -1 ] :
                    clientName = clientName + "-" 
        
        src         = self.imageName
        destination = PXPaths.GRAPHS + "/symlinks/%s.png" %clientName 
        
        if not os.path.isdir( PXPaths.GRAPHS + "/symlinks/" ):
            os.makedirs( PXPaths.GRAPHS + "/symlinks/", mode=0777 )
        
        if os.path.isfile( destination ):
            os.remove( destination )
        
        os.symlink( src, destination )
        
        
         
    def plot( self, createLink = False  ):
        """
            Used to plot gnuplot graphics. Settings used are
            slighly modified but mostly based on Plotter.py's
            plot function. 
            
        """
        
        if self.logger != None:
            self.logger.debug( "Call to plot received" )
        
        #Set general settings for graphs 
        color = 1
        nbGraphs = 0
         
        totalSize = ( 0.38 * len( self.stats )  * len( self.statsTypes ) )
        
        self.graph('set terminal png size 1280,768')
        self.graph( 'set size 1.0, %2.1f' % ( totalSize ) )
        
        self.graph( 'set linestyle 4 ')
        
        self.graph.xlabel( 'time (hours)' ) #, offset = ( "0.0"," -2.5" )
        
        self.graph( 'set grid')
        self.graph( 'set format y "%10.0f"' )
        self.graph( 'set xtics (%s)' % self.xtics)
        #self.graph( "set xtics rotate" )
        
        if self.type == 'lines':
            self.graph( 'set data style lines' )  
        elif self.type == 'impulses':
            self.graph( 'set data style impulses' )  
        elif self.type == 'boxes':
            self.graph( 'set data style boxes' )  
        elif self.type == 'linespoints':
            self.graph( 'set data style linespoints' )  
            
        
        #self.graph( 'set terminal png size 800,600' )
       
        self.imageName = self.buildImageName()

        #self.graph( "set autoscale" )
        self.graph( 'set output "%s"' % (  self.imageName ) )
        self.graph( 'set multiplot' ) 
        
        
        for i in range( len( self.stats ) ) :            
                       
            for j in range ( len ( self.statsTypes ) ):
                
                pairs        = self.getPairs( clientCount =i , statType= self.statsTypes[j], typeCount = j )
                maxPairValue = self.getMaxPairValue( pairs )
                self.maxLatency = self.stats[i].statsCollection.maxLatency
                
                if self.statsTypes[j] == "errors" :
                    color =2 #green
                    
                    self.addErrorsLabelsToGraph(  i , nbGraphs, j, maxPairValue )
                elif self.statsTypes[j] == "latency" :
                    color =1 #red
                    
                    self.addLatencyLabelsToGraph(  i , nbGraphs, j, maxPairValue )
                
                elif self.statsTypes[j] == "bytecount" :
                    color =3 #blue 
                    self.addBytesLabelsToGraph(  i , nbGraphs, j, maxPairValue )
                    
                self.graph.title( "%s" %self.buildTitle( i, self.statsTypes[j] , j ) )
                
                self.graph.plot( Gnuplot.Data( pairs , with="%s %s 1" % ( self.type, color) ) )
                
                nbGraphs = nbGraphs + 1 
                
                    
        if createLink :
            self.createLink( )     
         
            
            
    def addLatencyLabelsToGraph( self, i , nbGraphs, j, maxPairValue ):
        """
            Used to set proper labels for a graph relating to latencies. 
             
        """            
        
        if self.maximums[i][j] != None and self.maximums[i][j] !=0 :
            
            timeOfMax = self.timeOfMax[i][j] 
            
            if maxPairValue < 5 :
                self.graph( 'set format y "%7.2f"' )
            else:
                self.graph( 'set format y "%7.0f"' )
            
            maximum = self.maximums[i][j]
        
        else:
            timeOfMax = ""
            maximum = ""       
                  
                
        self.graph( 'set size .545, .37' )
        
        self.graph( 'set origin 0, %3.2f' %( ((nbGraphs)*.37)  ) )

        self.graph.ylabel( 'latency (seconds)' )
        
        self.graph( 'set label "Client : %s" at screen .545, screen %3.2f' % ( self.clientNames[i],(.28+(nbGraphs) *.37)  ))
        
        self.graph( 'set label "Machines : %s" at screen .545, screen %3.2f' % ( self.machines,(.26+(nbGraphs) *.37)  ) )
        
        self.graph( 'set label "Product Type : %s" at screen .545, screen %3.2f' % ( self.productType,(.24+(nbGraphs) *.37)  ) )
        
        self.graph( 'set label "Maximum latency : %s (Seconds)" at screen .545, screen %3.2f' % ( maximum, (.22+(nbGraphs) *.37) ) )
        
        self.graph( 'set label "Time of maximum latency : %s" at screen .545, screen %3.2f' % ( ( timeOfMax, (.20+(nbGraphs) *.37)  )))
        
        if len ( self.filesWhereMaxOccured[i][j] ) <= 50 :
            self.graph( 'set label "File with maximum latency :%s" at screen .545, screen %3.2f' % ( self.filesWhereMaxOccured[i][j], (.18+(nbGraphs) *.37) ))     
        
        else:
            self.graph( 'set label "File with maximum latency :" at screen .545, screen %3.2f' % ( (.18+(nbGraphs) *.37) ))  
            
            self.graph( 'set label "%s" at screen .545, screen %3.2f' % ( self.filesWhereMaxOccured[i][j], (.16+(nbGraphs) *.37 ) ))          
        
        self.graph( 'set label "# of files(total) : %s " at screen .545, screen %3.2f' % ( self.nbFiles[i] , (.14+(nbGraphs) *.37) ) )
        
        self.graph( 'set label "# of files over %s seconds: %s " at screen .545, screen %3.2f' % ( self.maxLatency, self.nbFilesOverMaxLatency[i], ( .12+(nbGraphs) *.37 ) ) )
        
        self.graph( 'set label "%% of files over max latency: %3.2f %%" at screen .545, screen %3.2f' % ( self.ratioOverLatency[i] , ( .10 + (nbGraphs) *.37 ) ) )
        
                
    
            
    def addBytesLabelsToGraph( self, i , nbGraphs, j, maxPairValue ):
        """
            Used to set proper labels for a graph relating to bytes. 
             
        """            
        
        if self.maximums[i][j] != None and self.maximums[i][j] != 0 :
            
            timeOfMax = self.timeOfMax[i][j] 
            
            if maxPairValue < 5 :
                self.graph( 'set format y "%7.2f"' )
            else:
                self.graph( 'set format y "%7.0f"' )    
                
            maximum = self.maximums[i][j]
        
        else:
            timeOfMax = ""
            maximum = ""
        
         
       
        self.graph( 'set size .545, .37' )
        
        self.graph( 'set origin 0, %3.2f' %( ((nbGraphs)*.37)  ))
        
        self.graph.ylabel( '# of Bytes' )
        
        self.graph( 'set label "Client : %s" at screen .545, screen %3.2f' % ( self.clientNames[i],(.28+(nbGraphs) *.37)  ))
        
        self.graph( 'set label "Machines : %s" at screen .545, screen %3.2f' % ( self.machines,(.25+(nbGraphs) *.37)  ) )
        
        self.graph( 'set label "Product Type : %s" at screen .545, screen %3.2f' % ( self.productType,(.22+(nbGraphs) *.37)  ) )
        
        
        if len ( self.filesWhereMaxOccured[i][j] ) <= 65 :            
            self.graph( 'set label "Largest file : %s" at screen .545, screen %3.2f' % ( self.filesWhereMaxOccured[i][j], (.19+(nbGraphs) *.37) ))
        else:
            self.graph( 'set label "Largest file : " at screen .545, screen %3.2f' % ( ( .19 + ( nbGraphs ) *.37) ) )
            
            self.graph( 'set label "%s" at screen .545, screen %3.2f' % ( self.filesWhereMaxOccured[i][j], (.17+(nbGraphs) *.37) ))
                    
        self.graph( 'set label "Size of largest file : %s (Bytes)" at screen .545, screen %3.2f' % ( maximum, (.15+(nbGraphs) *.37) ) )       
                
        self.graph( 'set label "Time of largest file : %s" at screen .545, screen %3.2f' % ( ( timeOfMax, (.12+(nbGraphs) *.37)  )))     
        
        self.graph( 'set label "# of files : %s " at screen .545, screen %3.2f' % ( self.nbFiles[i] , (.09+(nbGraphs) *.37) ) )
    
    
    
    
    def addErrorsLabelsToGraph( self, i , nbGraphs, j,maxPairValue ):
        """
            Used to set proper labels for a graph relating to bytes. 
             
        """   
                 
        if self.maximums[i][j] !=None and self.maximums[i][j] != 0 :
            
            timeOfMax =  self.timeOfMax[i][j]
            timeOfMax =  MyDateLib.getIsoWithRoundedSeconds( timeOfMax )
            
            if maxPairValue < 5 :
                self.graph( 'set format y "%7.2f"' )
            else:
                self.graph( 'set format y "%7.0f"' )
        
            maximum = self.maximums[i][j]
        
        else:
            timeOfMax = ""
            maximum = ""
               
       
        self.graph( 'set size .545, .37' )
        
        self.graph( 'set origin 0, %3.2f' %( ((nbGraphs)*.37)  ))
        
        self.graph.ylabel( '# of Errors' )
        
        self.graph( 'set label "Client : %s" at screen .545, screen %3.2f' % ( self.clientNames[i],(.28+(nbGraphs) *.37)  ))
        
        self.graph( 'set label "Machines : %s" at screen .545, screen %3.2f' % ( self.machines,(.25+(nbGraphs) *.37)  ) )
        
        self.graph( 'set label "Product Type : %s" at screen .545, screen %3.2f' % ( self.productType,(.22+(nbGraphs) *.37)  ) )
        
        self.graph( 'set label "Max error/%s : %s" at screen .545, screen %3.2f' % ( self.entryType, maximum, (.19+(nbGraphs) *.37) ))
        
        
        self.graph( 'set label "Time of maximum : %s" at screen .545, screen %3.2f' % ( ( timeOfMax, (.16+(nbGraphs) *.37)  )))
        
        self.graph( 'set label "# of errors : %s" at screen .545, screen %3.2f' % ( self.nbErrors[i], (.13+(nbGraphs) *.37) ) )
      
                
                
            




    
    
    