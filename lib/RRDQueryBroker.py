
#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.


##############################################################################
##
##
## @Name   : RRDQueryBroker.py 
##
##
## @author :  Nicholas Lemay
##
## @since  : 2007-06-28, last updated on 2007-07-03  
##
##
## @summary : This class implements the GraphicsQueryBrokerInterface
##            and allows to execute queries towards the rrd graphics
##            creator from a web interface.  
##
##            
##
## @requires: generateRRDGraphics.py 
##
##############################################################################
"""

import cgi, commands, os, sys
import cgitb; cgitb.enable()
sys.path.insert(1, sys.path[0] + '/../../')


from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.GraphicsQueryBrokerInterface import GraphicsQueryBrokerInterface

LOCAL_MACHINE = os.uname()[1]


class RRDQueryBroker(GraphicsQueryBrokerInterface):
    """
        Interface containing the list of methods
        wich need to be implemented by the class 
        wich implement the GraphicsQueryBroker.
          
    """
    
    def __init__(self,  query=None, reply = None, queryParameters = None, replyParameters = None, graphicProducer = None ):
        """
            @summary: GnuQueryBroker constructor.
            
            @param queryParameters: _QueryParameters instance wich 
                                    contains the query parameters. 
            
            @param replyParameters: _replyParameters instance wich contains the reply parameters.
             
            @param reply: Reply to send to querier
            
            @query : Query to send to generateRRDGraphics.py
              
        
        """       
        
        self.queryParameters = queryParameters
        self.query = query
        self.replyParameters = replyParameters
        self.reply = reply 
    
    
    
    class _QueryParameters(object):
        """
            List of parameters needed for queries.
        """
        
        
        
        def __init__( self, fileType, sourLients, groupName, machines, havingRun, individual, total, endTime,  products, statsTypes,  span, specificSpan, fixedSpan ):
            """
                @summary : _QueryParameters parameters class constructor.                
                
                @param fileType: rx or tx                
                @param sourLients: list of sour or clients for wich to produce graphic(s).                
                @param groupName: Group name tag to give to a group of clients.      
                @param machines : List of machine on wich the data resides.   
                @param havingRun: Use the sourlients having run during period instead of those currently running.
                @param individual: Whether or not to make individual graphics for every machines.
                @param total : Whether or not to  make a total of all the data prior to plotting the graphics.               
                @param endTime: time of query of the graphics                
                @param products: List of specific products for wich to plot graphics.                
                @param statsTypes : List of stats types for wich to create the graphics.
                @param span: span in hoursof the graphic(s).            
                @param specificSpan: Daily, weekly,monthly or yearly
                @param fixedSpan : fixedPrevious or fixedCurrent
                
            """
            
            self.fileType     = fileType
            self.sourLients   = sourLients
            self.groupName    = groupName
            self.machines     = machines
            self.havingRun    = havingRun
            self.individual   = individual
            self.total        = total
            self.endTime      = endTime
            self.products     = products
            self.statsTypes   = statsTypes
            self.span         = span
            self.specificSpan = specificSpan
            self.fixedSpan    = fixedSpan    
    
    
    class _ReplyParameters(object):
        """
            List of parameters required for replies.
        """
        
        def __init__( self, querier, plotter, image, fileType, sourLients, groupName, machines, havingRun, individual, total, endTime,  products, statsTypes,  span, specificSpan, fixedSpan, error ):
            """
                @summary : _QueryParameters parameters class constructor.    
                            
                @param querier:Path to the program that sent out the request.
                @param plotter : Type of plotter that was selected.
                @param image   : image(s) that was/were produced by the plotter. 
                @param fileType: rx or tx                
                @param sourLients: list of sour or clients for wich to produce graphic(s).                
                @param groupName: Group name tag to give to a group of clients.      
                @param machines : List of machine on wich the data resides.   
                @param havingRun: Use the sourlients having run during period instead of those currently running.        
                @param individual: Whether or not to make individual graphics for every machines.
                @param total : Whether or not to  make a total of all the data prior to plotting the graphics.               
                @param endTime: time of query of the graphics                
                @param products: List of specific products for wich to plot graphics.                
                @param statsTypes : List of stats types for wich to create the graphics.
                @param span: span in hoursof the graphic(s).            
                @param specificSpan: Daily, weekly,monthly or yearly
                @param fixedSpan : fixedPrevious or fixedCurrent
                @param error : error that has occured during request.
            """
            
            self.querier      = querier
            self.plotter      = plotter 
            self.image        = image
            self.fileType     = fileType
            self.sourLients   = sourLients
            self.groupName    = groupName
            self.machines     = machines
            self.havingRun    = havingRun
            self.individual   = individual
            self.total        = total
            self.endTime      = endTime
            self.products     = products
            self.statsTypes   = statsTypes
            self.span         = span
            self.specificSpan = specificSpan
            self.fixedSpan    = fixedSpan    
            self.error        = error 
    
        
    def getParametersFromForm(self, form):
        """
             @summary: Initialises the queryParameters and 
                       reply parameters based on the form 
                       received as parameter. 
        """
        
        #Every param is set in an array, use [0] to get first item, nothing for array.
        try:
            querier = form["querier"]
        except:
            querier = ""
        
        try :    
            plotter = form["plotter"] 
        except:
            plotter = ""
            
        image        = None
        
        try:    
            fileTypes = form["fileType"].split(',')
        except:
            fileTypes = []
            
        try :
            sourLients = form["sourLients"].split(',')
        except:
            sourLients = []
        
        try :
            groupName = form["groupName"]        
        except:
            groupName = ""
        
        try:
            machines = form["machines"].split(',')
        except:
            machines = []
            
        try:
            havingRun = form["havingRun"]
        except:
            havingRun = 'false'
        
        try:    
            individual = form["individual"]        
        except:
            individual = 'false'
        
        try:
            total = form["total"]     
        except:
            total = 'false'
            
        try:
            endTime = form["endTime"]
        except:
            endTime = ''
        
        
        
        try :    
            products     = form["products"].split(',')
        except:
            products     = []
        
        try:
            statsTypes   = form["statsTypes"].split(',')
        except:
            statsTypes = []
        
        try:
            span = form["span"][0] 
        except:
            span = 24
        
        try:
            specificSpan = form["preDeterminedSpan"]
        except:
            specificSpan = ''
        
        try:    
            fixedSpan = form["fixedSpan"]
        except:
            fixedSpan = ''
                
        self.queryParameters = RRDQueryBroker._QueryParameters(fileTypes, sourLients, groupName, machines, havingRun, individual, total, endTime, products, statsTypes, span, specificSpan, fixedSpan)
        self.replyParameters = RRDQueryBroker._ReplyParameters(querier, plotter, image, fileTypes, sourLients, groupName, machines, havingRun, individual, total, endTime, products, statsTypes, span, specificSpan, fixedSpan, error = '' )
        
        
    def getParameters(self, parser, form):
        """
            @summary : Get parameters from either a form or a parser. 
                       Both need to have parameter names wich are the 
                       same as the ones used in the _QueryParameters
                       class.  
        """
        
        if form != None:
             self.getParametersFromForm( form )
    
    
    
    def searchForParameterErrors(self):
        """
            @summary : Validates parameters.
           
            @return  : Returns the first error 
                       found within the current
                       query parameters. 
        """
        
        error = ""
           
        try :
            
            if self.queryParameters.plotter != "rrd":
                error = "Internal error. GnuQueryBroker was not called to plota gnuplot graphic."
                raise
        
            for filetype in self.queryParameters.fileTypes :
                if fileType != "tx" and fileType != "rx":
                    error = "Error. FileType needs to be either rx or tx."
                    raise
                
            if self.queryParameters.sourLients == []:
                error = "Error. At least one sourlient needs to be specified."
                raise 
            
            if self.queryParameters.machines == []:
                error = "Error. At least one machine name needs to be specified."
                raise
            
            if self.queryParameters.combine != 'true' and self.queryParameters.combine != 'false':
                error = "Error. Combine sourlients option needs to be either true or false."  
                raise
            
            if self.queryParameters.statsTypes == []:
                error = "Error. At Leat one statsType needs to be specified."   
                raise
            
            if self.queryParameters.groupName != "" and self.queryParameters.total != 'true':
                error = "Error. Groupname needs to be used with total option."
                raise 
            
            if self.queryParameters.groupName != "" and self.queryParameters.individual == 'true':
                error = "Error. Groupname cannot be used with individual option."
                raise
            
            if self.queryParameters.fixedSpan != "" and self.specificSpan == "":
                error = "Error. Fixed spans need to be used with a specific spans."
                raise
            
            try:
                int(self.queryParameters.span)
            except:
                error = "Error. Span(in hours) value needs to be numeric."          
                raise
        except:
            
            pass
        
        
        return error     
    


    def prepareQuery(self):
        """
            @summary : Buildup the query  to be executed.
        
            @SIDE_EFFECT :  modifies self.query value.
            
        """
       
        
        pathToGenerateRRDGraphs = StatsPaths.STATSBIN + "generateRRDGraphics.py"
        
        if self.queryParameters.groupName != '':
            sourlients = '-c %s' %self.queryParameters.groupName
        elif self.queryParameters.sourLients !=[] :
            sourlients = '-c '
            for sourLient in self.queryParameters.sourLients:
                sourlients = sourlients + sourLient + ','
            sourlients = sourlients[:-1]
        else:
            sourlients = ''
        
                
        hour      = self.queryParameters.endTime.split(" ")[1]
        splitDate = self.queryParameters.endTime.split(" ")[0].split( '-' )
        
        date = "--date '%s'" %( splitDate[2] + '-' + splitDate[1]  + '-' + splitDate[0]  + " " + hour )
        
        fileType = '-f %s' %( str( self.queryParameters.fileType).replace('[','').replace( ']', '' ) )
        
        combinedMachineName = ""
        for machine in self.queryParameters.machines:
            combinedMachineName = combinedMachineName + ','+ machine 
        combinedMachineName = combinedMachineName[1:]    
        machines = '--machines %s' %( combinedMachineName )
        
        #optional option
        if self.queryParameters.specificSpan == "daily":
            specificSpan = "-d"
        elif self.queryParameters.specificSpan == "weekly":
            specificSpan = "-w"        
        elif self.queryParameters.specificSpan == "monthly":
            specificSpan = "-m"
        elif self.queryParameters.specificSpan == "yearly":
            specificSpan = "-y"
        else:
            specificSpan = ""      
        
        if self.queryParameters.fixedSpan == "fixedCurrent" :
            fixedSpan = "--fixedCurrent"
        elif self.queryParameters.fixedSpan == "fixedPrevious":
            fixedSpan = "--fixedPrevious"     
        else:
            fixedSpan = ""
            
        if self.queryParameters.havingRun == 'true':
            havingRun = "--havingrun"
        else:
            havingRun = ""
        
        if self.queryParameters.individual == 'true':
            individual = '--individual'
        else:
            individual = ''    
        
        if self.queryParameters.total == 'true' :
            total = '--total'
        else:
            total = ''    
        
        if self.queryParameters.statsTypes !=[] and self.queryParameters.statsTypes != '':
            statsTypes = '-t '
            for type in self.queryParameters.statsTypes:
                statsTypes = statsTypes + type + ','
            types = statsTypes[:-1]
                   
        else:
            types = ''
            
        self.query = "%s %s %s %s %s %s %s %s %s %s %s --turnOffLogging" %( pathToGenerateRRDGraphs, sourlients, machines, date, fileType, fixedSpan, specificSpan, havingRun, total, individual, types)
            
           
            
    def getImagesFromQueryOutput( self, output ):
        """ 
            @summary : Parses the output and retreives 
                       the name of images that were plotted.
            
            @return: Returns the list of images
            
        """
        
        images = ''
        
        lines = output.splitlines()
        
        for line in lines :
            if  "Plotted" in line:
                #print line 
                imageName = line.replace( "Plotted :", "").replace( " ", "")
                imageName = '../../pxStats' + imageName.split( 'pxStats' )[1] 
                images = images + imageName + ','
                
        images = images[:-1]    
        #print images
        return images 
    
    
    
    def executeQuery(self):
        """
            @summary : Simply Execute the query stored in self.query.
            
            @SIDE-EFECT : Will set the name of the generated images in self.replyparameters.image
            
        """
        #print self.query
        status, output = commands.getstatusoutput( self.query )  
       
        self.replyParameters.image = self.getImagesFromQueryOutput(output)
    
    
    
    def getReplyToSendToquerier(self):
        """
           @summary: Returns the reply of the query to send to the querier.
           
           @return: The query
           
        """
        
        params = self.replyParameters
        
        reply = "images=%s;error=%s" %(  params.image,  params.error )
        
        
        # reply = "?plotter=%s&?image=%s&fileType=%s&sourlients=%s&groupName=%s&machines=%s&individual=%s&total=%s&endTime=%s&products=%s&statsTypes=%s&span=%s&specificSpan=%s&fixedSpan=%s" \
         # %( params.plotter, params.image, params.fileType, params.sourLients, params.groupName,
            # params.machines, params.individual, params.total, params.endTime, params.products, params.statsTypes, params.span, params.specificSpan, params.fixedSpan  )
        #----------------------------------------------------------- print reply
        
        return reply
        
        
        
        
        