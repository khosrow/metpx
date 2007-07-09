#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.


##############################################################################
##
##
## @Name   : GnuQueryBroker.py 
##
##
## @author :  Nicholas Lemay
##
## @since  : 2007-06-28, last updated on  2007-07-03
##
##
## @summary : This class implements the GraphicsQueryBrokerInterface
##            and allows to execute queries towards the gnuplot graphics
##            creator from a web interface.     
##
##            
##
## @requires: GraphicsQueryBrokerInterface, wich it implements. 
##            
##
##############################################################################
"""
import cgi, os, sys
import cgitb; cgitb.enable()
sys.path.insert(1, sys.path[0] + '/../../')


from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods



class GnuQueryBroker(GraphicsQueryBrokerInterface):
    """    
        @summary: This class implements the GraphicsQueryBrokerInterface
                  and allows to execute queries towards the gnuplot graphics
                  creator from a web interface.          
    
    """    
    
    def __init__(self, queryParameters = None, replyParameters = None, graphicProducer = None ):
        """
            @summary: GnuQueryBroker constructor.
            
            @param queryParameters: _QueryParameters instance wich 
                                    contains the query parameters. 
            
            @param graphicProducer:  
        
        """
        
        self.queryParameters = queryParameters
        self.graphicProducer = graphicProducer
        self.replyParameters = replyParameters
    
    
    
    class _QueryParameters(object):
       
        def __init__( self, fileType, sourLients, groupName, machines, combine, endTime,  products, statsTypes,  span ):
            """
                @summary : _QueryParameters parameters class constructor.                
                
                @param fileType: rx or tx                
                @param sourLients: list of sour or clients for wich to produce graphic(s).                
                @param groupName: Group name tag to give to a group of clients.      
                @param machines : List of machine on wich the data resides.           
                @param combine: Whether or not( true or false ) to combine the sourlients.                
                @param endTime: time of query of the graphics                
                @param products: List of specific products for wich to plot graphics.                
                @param statsTypes : List of stats types for wich to create the graphics.
                @param span: span in hoursof the graphic(s).            
            
            """
            
            self.fileType   = fileType
            self.sourLients = sourLients
            self.groupName  = groupName
            self.machines   = machines
            self.combine    = combine
            self.endTime    = endTime
            self.products   = products
            self.statsTypes = statsTypes
            self.span       = span
        
        
            
    class _ReplyParameters( _QueryParameters ):   
        
        def __init__( self, querier, plotter, image, fileType, sourLients, groupName, machines, combine, endTime,  products, statsTypes,  span ):    
            """
                @summary : _ReplyParameters parameters class constructor.                
                
                @param querier: Path to the program that sent out the query.
                @param plotter: Type of plotter that was selected.
                @param image:   Path to the image that was created. 
                @param fileType: rx or tx                
                @param sourLients: list of sour or clients for wich to produce graphic(s).                
                @param groupName: Group name tag to give to a group of clients.      
                @param machines : List of machine on wich the data resides.           
                @param combine: Whether or not( true or false ) to combine the sourlients.                
                @param endTime: time of query of the graphics                
                @param products: List of specific products for wich to plot graphics.                
                @param statsTypes : List of stats types for wich to create the graphics.
                @param span: span in hoursof the graphic(s). 
            
            """           
            
            self.querier    = querier
            self.plotter    = plotter
            self.image      = image
            self.fileType   = fileType
            self.sourLients = sourLients
            self.groupName  = groupName
            self.machines   = machines
            self.combine    = combine
            self.endTime    = endTime
            self.products   = products
            self.statsTypes = statsTypes
            self.span       = span
                    
      
       
    def getParametersFromParser( self, parser ):
        """
            @summary : Uses the parser to gather the 
                       parameters from a call from the
                       command line.
        """  
        x =2 
        
        
        
    def getParametersFromForm( self, form ):
        """
            @summary: Initialises the queryParameters
                      based on the form received as 
                     parameter.         
        """
        
        #Every param is set in an array, use [0] to get first item, nothing for array.
        querier     = form["querier"][0]
        plotter     = form["plotter"][0] 
        image       = None
        fileTypes   = form["fileType"]
        sourLients  = form["sourLients"]
        groupName   = form["groupName"][0]
        machines    = form["machines"]
        combine     = form["combineSourlients"][0]
        endTime     = form["endTime"][0]
        products    = form["products"]
        statsTypes  = form["statsTypes"]
        span        = form["span"][0]
        
        self.queryParameters = _QueryParameters( fileType, sourLients, groupName, machines, combine, endTime,  products, statsTypes,  span )
        
        self.replyParameters = _ReplyParameters( querier, plotter, image, fileTypes, sourLients, groupName, machines, combine, endTime,
                                                 products, statsTypes,  span )
        
        
        
    def getParameters( self, querier, form , parser ):
        """
            @summary : Get parameters from either a form or a parser. 
                       Both need to have parameter names wich are the 
                       same as the ones used in the _QueryParameters
                       class.  
        
        """        
        
        if form != None: 
            self.getParametersFromForm( form )
        elif parser != None :
            self.getParametersFromParser( parser )
    
    
    
    def searchForParameterErrors(self):
        """
            @summary : Validates parameters.
           
            @return  : Returns the first error 
                       found within the current
                       query parameters. 
        """
        
        error = ""
        
        try :
            
            if self.queryParameters.plotter != "gnuplot":
                error = "Internal error. GnuQueryBroker was not called to plota gnuplot graphic."
                raise
        
            for filetype in self.queryParameters.fileTypes :
                if fileType != "tx" and fileType != "rx":
                    error = "Error. FileType needs to be either rx or tx."
                    raise
            if self.queryParameters.sourLients == []:
                error = "Error. At least one sourlient needs to be specified."
            
            if self.queryParameters.machines == []:
                error = "Error. At least one machine name needs to be specified."
            
            if self.queryParameters.combine != 'true' and self.queryParameters.combine != 'false':
                error = "Error. Combine sourlients option needs to be either true or false."  
            
            if self.queryParameters.statsTypes == []:
                error = "Error. At Leat one statsType needs to be specified."   
            
            try:
                int(self.queryParameters.span)
            except:
                error = "Error. Span(in hours) value needs to be numeric."          
                
        except:
            
            pass
        
        
        return error  


    
    def prepareQuery(self):
        """
            Buildup the query line to be executed.
        """
        
        directory = GeneralStatsLibraryMethods.getPathToLogFiles( LOCAL_MACHINE, self.queryParameters.machines[0] )
        
        
        self.graphicProducer = ClientGraphicProducer( directory = directory, fileType = self.queryParameters.fileType,  
                                                      clientNames = self.queryParameters.sourLients, 
                                                      groupName = self.queryParameters.groupName, 
                                                      timespan = self.queryParameters.span, currentTime = self.queryParameters.endtime,
                                                      productTypes = self.queryParameters.products, logger= NONE,
                                                      machines = self.queryParameters.machines )
       
      
    
    
    
    def executeQuery(self):
        """
            @summary: Execute the built-up query on the needed plotter.
            
            @side-effect : Will set the name of the produced image in the reply parameters.
        
        """
         
        imageName = self.graphicProducer.produceGraphicWithHourlyPickles( types = self.queryParameters.statsTypes , now = False, 
                                                              createCopy = False, combineClients = self.queryParameters.combine )
    
        self.replyParameters.image = imageName
    
    
    
    def getReplyToSendToquerier(self):
        """
            @summary : Builds the reply to send to the querier.
            
            @return: The reply.
        
        """
        
        params = self.replyParameters
        
        reply = "?plotter=%s&?image=%s&fileType=%s&sourlients=%s&groupName=%s&machines=%s&combineSourlients=%s&%endTime=%s&products=%s&statsTypes=%s&span=%s" \
         %( params.plotter, params.image, params.fileType, params.sourLients, params.groupName,
            params.machines, params.combine, params.endtime, params.products, params.statsTypes, params.span  )
         
        return reply
    
    
    
    
       