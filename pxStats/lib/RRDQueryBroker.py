
#! /usr/bin/env python
"""
##############################################################################
##
##
## @Name   : RRDQueryBroker.py 
##
##
## @author :  Nicholas Lemay
##
## @license: MetPX Copyright (C) 2004-2006  Environment Canada
##           MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
##           named COPYING in the root of the source directory tree.
##
## @since  : 2007-06-28, last updated on 2008-04-23  
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

import cgi, commands, gettext, os, sys
import cgitb; cgitb.enable()
sys.path.insert(1,  os.path.dirname( os.path.abspath(__file__) ) + '/../../')


from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.GraphicsQueryBrokerInterface import GraphicsQueryBrokerInterface
from pxStats.lib.RRDGraphicProducer import RRDGraphicProducer
from pxStats.lib.LanguageTools import LanguageTools
from pxStats.lib.StatsDateLib import StatsDateLib


LOCAL_MACHINE = os.uname()[1]

CURRENT_MODULE_ABS_PATH =  os.path.abspath(__file__).replace( ".pyc", ".py" )


class RRDQueryBroker(GraphicsQueryBrokerInterface):
    """
         Class which implements the GraphicsQueryBrokerInterface and allows 
         us to produce graphics using the RRDGraphicProducer class.
          
    """    
    
    def __init__( self, querierLanguage, queryParameters = None, replyParameters = None,
                  graphicProducer = None,  ):
        """
            @summary: RRDQueryBroker constructor.
            
            @param querierLanguage : Language spoken by the qerier at the time of the query.
            
            @param queryParameters: _QueryParameters instance wich 
                                    contains the query parameters. 
            
            @param replyParameters: _replyParameters instance wich contains the reply parameters.           

        """               
        
        self.queryParameters = queryParameters
        self.replyParameters = replyParameters
        self.graphicProducer = graphicProducer
        self.querierLanguage = querierLanguage
        
        if self.querierLanguage not in LanguageTools.getSupportedLanguages():
            raise Exception( "Error. Unsupported language detected in RRDQueryBroker. %s is not a supported language."%( self.querierLanguage ) )
        else:#language is supposed to be supported 
            global _
            _ = self.getTranslatorForModule( CURRENT_MODULE_ABS_PATH, self.querierLanguage )
        
  
        
    class _QueryParameters(object):
        """
            List of parameters needed for queries.
        """
        
        
        
        def __init__( self, fileTypes, sourLients, groupName, machines, havingRun, individual, combine, endTime,  products, statsTypes,  span, specificSpan, fixedSpan ):
            """
                @summary : _QueryParameters parameters class constructor.                
                
                @param fileTypes: list of rx or tx                
                @param sourLients: list of sour or clients for wich to produce graphic(s).                
                @param groupName: Group name tag to give to a group of clients.      
                @param machines : List of machine on wich the data resides.   
                @param havingRun: Use the sourlients having run during period instead of those currently running.
                @param individual: Whether or not to make individual graphics for every machines.
                @param combine : Whether or not to  make a combine of all the data prior to plotting the graphics.               
                @param endTime: time of query of the graphics                
                @param products: List of specific products for wich to plot graphics.                
                @param statsTypes : List of stats types for wich to create the graphics.
                @param span: span in hoursof the graphic(s).            
                @param specificSpan: Daily, weekly,monthly or yearly
                @param fixedSpan : fixedPrevious or fixedCurrent
                
            """
            
            self.fileTypes    = fileTypes
            self.sourLients   = sourLients
            self.groupName    = groupName
            self.machines     = machines
            self.havingRun    = havingRun
            self.individual   = individual
            self.combine      = combine
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
        
        def __init__( self, querier, plotter, image, fileTypes, sourLients, groupName, machines, havingRun, individual,
                      combine, endTime,  products, statsTypes,  span, specificSpan, fixedSpan, error ):
            """
                @summary : _QueryParameters parameters class constructor.    
                            
                @param querier:Path to the program that sent out the request.
                @param plotter : Type of plotter that was selected.
                @param image   : image(s) that was/were produced by the plotter. 
                @param fileTypes: rx or tx                
                @param sourLients: list of sour or clients for wich to produce graphic(s).                
                @param groupName: Group name tag to give to a group of clients.      
                @param machines : List of machine on wich the data resides.   
                @param havingRun: Use the sourlients having run during period instead of those currently running.        
                @param individual: Whether or not to make individual graphics for every machines.
                @param combine : Whether or not to  make a combine of all the data prior to plotting the graphics.               
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
            self.fileTypes    = fileTypes
            self.sourLients   = sourLients
            self.groupName    = groupName
            self.machines     = machines
            self.havingRun    = havingRun
            self.individual   = individual
            self.combine      = combine
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
            combine = form["combineSourlients"].replace(",", "").replace('"','')  
        except:
            combine = 'false'
            
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
            
        #statsTypes = translateStatsTypes( statsTypes ) 
        
        try:
            span = form["span"]
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
                
        self.queryParameters = RRDQueryBroker._QueryParameters(fileTypes, sourLients, groupName, machines, havingRun, individual, combine, endTime, products, statsTypes, span, specificSpan, fixedSpan)
        self.replyParameters = RRDQueryBroker._ReplyParameters(querier, plotter, image, fileTypes, sourLients, groupName, machines, havingRun, individual, combine, endTime, products, statsTypes, span, specificSpan, fixedSpan, error = '' )
        
    
    #----------------------------------- def translateStatsTypes( statsTypes ) :
        #------------------------------------------------------------------- """
            #------------------------------- @summary : Takes a list of statypes
#------------------------------------------------------------------------------ 
            #--------------------- @return : The list of translated stats types.
#------------------------------------------------------------------------------ 
        #------------------------------------------------------------------- """
#------------------------------------------------------------------------------ 
        #---------------------------------------------- translatedStatTypes = []
#------------------------------------------------------------------------------ 
        # statsTypesTranslations = { _("latency"):"latency", _("bytecount"):"bytecount", _("filecount"):"filecount", _("errors"):"errors" }
#------------------------------------------------------------------------------ 
        #--------------------------------- for i in range( len( statsTypes ) ) :
            # translatedStatTypes.append( statsTypesTranslations[ statsTypes[i] ] )
#------------------------------------------------------------------------------ 
        #-------------------------------------------- return translatedStatTypes
    
    
    
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
        
        global _ 
        
        error = ""
           
        try :
            
            if self.queryParameters.plotter != "rrd":
                error = _("Internal error. RRDQueryBroker was not called to plot a rrd graphic.")
                raise
        
            for fileType in self.queryParameters.fileTypes :
                if fileType != "tx" and fileType != "rx":
                    error = _("Error. FileType needs to be either rx or tx.")
                    raise
                
            if self.queryParameters.sourLients == []:
                error = _("Error. At least one sourlient needs to be specified.")
                raise 
            
            if self.queryParameters.machines == []:
                error = _("Error. At least one machine name needs to be specified.")
                raise
            
            if self.queryParameters.combine != 'true' and self.queryParameters.combine != 'false':
                error = _("Error. Combine sourlients option needs to be either true or false."  )
                raise
            
            if self.queryParameters.statsTypes == []:
                error = _("Error. At Leat one statsType needs to be specified."  ) 
                raise
                        
            if self.queryParameters.groupName != "" and self.queryParameters.individual == 'true':
                error = _("Error. Groupname cannot be used with individual option.")
                raise
            
            if self.queryParameters.fixedSpan != "" and self.specificSpan == "":
                error = _("Error. Fixed spans need to be used with a specific spans.")
                raise
            
            try:
                int(self.queryParameters.span)
            except:
                error = _("Error. Span(in hours) value needs to be numeric.")
                raise
        except:
            
            pass
        
        
        return error     
    


    def prepareQuery(self):
        """
            @summary : Buildup the query  to be executed.
        
            @SIDE_EFFECT :  modifies self.query value.
            
        """
        
        global _ 
        
        if self.queryParameters.combine == 'true':
            totals = True
            mergerType = "regular"
        else:
            totals = False      
            mergerType = ""
            
            
        fixedCurrent  = False
        fixedPrevious = False
        
        if _("current")  in str(self.queryParameters.fixedSpan).lower() :
            fixedCurrent = True 
        elif _("previous") in str(self.queryParameters.fixedSpan).lower():
            fixedPrevious = True      
        else:
            fixedCurrent  = False
            fixedPrevious = False 
       

            
        hour      = self.queryParameters.endTime.split(" ")[1]
        splitDate = self.queryParameters.endTime.split(" ")[0].split( '-' )
        
        date =  splitDate[2] + '-' + splitDate[1]  + '-' + splitDate[0]  + " " + hour 
        if self.queryParameters.span == "": 
            timespan = 0 
        else:
            timespan = int(self.queryParameters.span )    
            
        StatsDateLib.setLanguage( self.querierLanguage )
        startTime, endTime = StatsDateLib.getStartEndInIsoFormat(date, timespan, self.queryParameters.specificSpan, fixedCurrent, fixedPrevious )
        
        timespan = int( StatsDateLib.getSecondsSinceEpoch( endTime ) - StatsDateLib.getSecondsSinceEpoch( startTime ) ) / 3600   
               
        
        self.graphicProducer = RRDGraphicProducer( self.queryParameters.fileTypes[0], self.queryParameters.statsTypes ,\
                                                   totals,  self.queryParameters.specificSpan,\
                                                   self.queryParameters.sourLients, timespan,\
                                                   startTime, endTime, self.queryParameters.machines, False,
                                                   mergerType, True, self.querierLanguage, self.querierLanguage )
  
        StatsDateLib.setLanguage( LanguageTools.getMainApplicationLanguage() )
            
            
            
    def getImageListToReplyFromPlottedImageList( self, plottedImages ):
        """ 
            @summary : Transforms the list of plotted images in a string we can use 
                       in the reply.
            
            @return: Returns the list of images
            
        """
        
        images = ''
                
        for imageName in plottedImages :
            images = images + '../../pxStats' + imageName.split( 'pxStats' )[-1:][0] + '+'
                
        images = images[:-1]    
        #print images
        
        return images 
    
    
    
    def executeQuery(self):
        """
            @summary : Simply Execute the query stored in self.query.
            
            @SIDE-EFECT : Will set the name of the generated images in self.replyparameters.image
            
        """
       
        plottedImages = self.graphicProducer.generateRRDGraphics()
    
        self.replyParameters.image = self.getImageListToReplyFromPlottedImageList( plottedImages )
    
    
    
    def getReplyToSendToquerier(self):
        """
           @summary: Returns the reply of the query to send to the querier.
           
           @return: The query
           
        """
        
        params = self.replyParameters
        
        if params.image == '':
            params.error = 'Error. Could not produce image with the specified parameters.' 
            
        reply = "images=%s;error=%s" %(  params.image,  params.error )
        
        
        # reply = "?plotter=%s&?image=%s&fileType=%s&sourlients=%s&groupName=%s&machines=%s&individual=%s&total=%s&endTime=%s&products=%s&statsTypes=%s&span=%s&specificSpan=%s&fixedSpan=%s" \
         # %( params.plotter, params.image, params.fileType, params.sourLients, params.groupName,
            # params.machines, params.individual, params.total, params.endTime, params.products, params.statsTypes, params.span, params.specificSpan, params.fixedSpan  )
        #----------------------------------------------------------- print reply
        
        return reply
        
        
        
        
        