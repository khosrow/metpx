#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.


##############################################################################
##
##
## @Name   : graphicsRequestBroker.py 
##
##
## @author :  Nicholas Lemay
##
## @since  : 2007-06-28, last updated on  
##
##
## @summary : This file is to be used as a bridge between the graphics 
##            request web page  and hte different plotting methods.
##
##            
##
## @requires: graphicsRequest, wich sends all the queries. 
##            
##            The different graphic plotters.
##
##
##############################################################################
"""

import cgi, os, sys
import cgitb; cgitb.enable()

sys.path.insert(1, sys.path[0] + '/../../../')
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.ClientGraphicProducer import ClientGraphicProducer
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.GnuQueryBroker import GnuQueryBroker
from pxStats.lib.RRDQueryBroker import RRDQueryBroker

LOCAL_MACHINE = os.uname()[1]


def returnToQueriersLocationWithReply( querier, reply ):
    """
        @summary : Changes location back to the querier + returns the 
                   reply of the query to the querier.
                   
        @param querier: String containing the location of the querier.
        
        @param reply : Series of parameters to send as a reply to te querier.
        
    
    """
    print """Content-Type: text/html"""
    print "Location: " + querier + reply #Return location to querier with reply....
 
 
def getQuerierLocation( form ):
    """ 
        @param form : Form with whom this programm was called.
    
        @return : Returns the queriers location.
         
    """   
    
    return form["querier"].value
    
    
    
def handlePlotRequest( form ): 
    """
        @param form: form wich contains 
                     the parameters to use
                     for the query.
    """
    
    querier =  getQuerierLocation( form ) 
    plotter = getPlotterType(form)
    
    if plotter == "gnuplot":
        queryBroker = GnuQueryBroker()
    elif plotter == "rrd":
        queryBroker = RRDQueryBroker()
        
    
    queryBroker.getParametersFromForm( form )
    error =queryBroker.searchForParameterErrors()
    
    if error == "" :
        queryBroker.prepareQuery( )
        queryBroker.executeQuery( )
        reply = queryBroker.getReplyToSendToquerier()
    
    else: #An error was located within the call.
        reply = queryBroker.getReplyToSendToquerier()
        reply = reply + "&error=%s" %error
        
    returnToQueriersLocationWithReply( querier , reply )
  
 
   
def getPlotterType( form ): 
    """
        @param form : Form with whom this programm was called.
    
        @return : Returns the plotter type.
         
    """    
    
    return form["plotter"][0]
 
 
 
def getForm():
    """
        @summary: Returns the form with whom this page was called. 
        @return:  Returns the form with whom this page was called. 
    """
    form = cgi.FormContent()
    
    for key in form.keys():
        if "?" in key:
            form[key.replace("?","")]= form[key]
            
    print form
    return  form
     
     
 
def main():
    """
        @summary: Based on the plotter specified in the received form,
                  executes query using a broker that's specific to 
                  the said plotter.
    """
    
    form = getForm()
    
    plotterType = getPlotterType( form )
    
    handlePlotRequest(form)
          
        
    
if __name__ == '__main__':
    main()