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
## @since  : 2007-06-28, last updated on  2007-07-17 
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

sys.path.insert(1, sys.path[0] + '/../../')
sys.path.insert(2, sys.path[0] + '/../../..')

from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.ClientGraphicProducer import ClientGraphicProducer
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.GnuQueryBroker import GnuQueryBroker
from pxStats.lib.RRDQueryBroker import RRDQueryBroker
from cgi import escape
LOCAL_MACHINE = os.uname()[1]


def returnToQueriersLocationWithReply( querier, reply ):
    """
        @summary : Changes location back to the querier + returns the 
                   reply of the query to the querier.
                   
        @param querier: String containing the location of the querier.
        
        @param reply : Series of parameters to send as a reply to te querier.
        
    
    """
    
    print """
        HTTP/1.0 200 OK
        Server: NCSA/1.0a6
        Content-type: text/plain

    """   
    print """%s"""  %( escape(reply) )
    
    
 
 
def getQuerierLocation( form ):
    """ 
        @param form : Form with whom this programm was called.
    
        @return : Returns the queriers location.
         
    """   
    
    
    try:
        querier = form["querier"]
    except:
        querier = "" 
        
    return querier
    
    
def handlePlotRequest( form ): 
    """
        @param form: form wich contains 
                     the parameters to use
                     for the query.
    """
    
    querier =  getQuerierLocation( form ) 
    plotter = getPlotterType(form)
    
    #validate for known plotter
    if plotter == "gnuplot":
        queryBroker = GnuQueryBroker()
    elif plotter == "rrd":
        queryBroker = RRDQueryBroker()
    else:
        queryBroker = None    
    
    try:
        if queryBroker != None :#if valid plotter
            queryBroker.getParametersFromForm( form )
            error = queryBroker.searchForParameterErrors()
            
            if error == "" :
                queryBroker.prepareQuery( )
                queryBroker.executeQuery( )
                reply = queryBroker.getReplyToSendToquerier()
                returnToQueriersLocationWithReply( querier , reply )
                
            else: #An error was located within the call.
                queryBroker.replyParameters.error = error
                reply = queryBroker.getReplyToSendToquerier()
                returnToQueriersLocationWithReply( querier , reply )
        
        else:#other
            reply = "images=;error=Cannot execute query.Unknown plotter.Plotter was %s" %plotter
            returnToQueriersLocationWithReply( querier , reply )
         
    except Exception,inst:
        reply = "images=;error=Unexpected error : %s." %(inst)
        returnToQueriersLocationWithReply( querier , reply )
   
   
def getPlotterType( form ): 
    """
        @param form : Form with whom this programm was called.
    
        @return : Returns the plotter type.
         
    """    
    try:
        plotter = form["plotter"]
    except:
        plotter = ""
        
    return plotter 
 
 
 
def getForm():
    """
        @summary: Returns the form with whom this page was called. 
        
        @note: The input form is expected ot be contained within the field storage. 
               Thus this program is expected to be called from requests like 
               xmlhttp.send()
        
        @return:  Returns the form with whom this page was called. 
    
    """
    
    newForm = {}
    form = cgi.FieldStorage()
    
    for key in form.keys():
        value = form.getvalue(key, "")
        if isinstance(value, list):
            # Multiple username fields specified
            newvalue = ",".join(value)
        else:
            newvalue = value
        
        newForm[key.replace("?","")]= newvalue
          
    form = newForm
           
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