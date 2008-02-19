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
## @since  : 2007-06-28, last updated on  2008-02-19 
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

import cgi, gettext, os, sys
import cgitb; cgitb.enable()

sys.path.insert(1, sys.path[0] + '/../../')
sys.path.insert(2, sys.path[0] + '/../../..')

from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.GnuQueryBroker import GnuQueryBroker
from pxStats.lib.RRDQueryBroker import RRDQueryBroker
from pxStats.lib.LanguageTools import LanguageTools
from cgi import escape



LOCAL_MACHINE = os.uname()[1]

EXPECTED_PARAMETERS = [ 'lang', 'querier','endTime','groupName','span','fileType','machines','statsTypes','preDeterminedSpan','sourlients','combineSourlients','products']

CURRENT_MODULE_ABS_PATH = os.path.abspath( sys.path[0] ) + '/' + "graphicsRequestBroker.py" 


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
    print """
            %s
    
    """  %( escape(reply) )
    
    
 
 
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
    
    #---------------------------------------------------------------------- try:
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
        reply = "images=;error=" + _("Cannot execute query.Unknown plotter.Plotter was %s") %plotter
        returnToQueriersLocationWithReply( querier , reply )
         
    #---------------------------------------------------- except Exception,inst:
        #---------------- reply = "images=;error=Unexpected error : %s." %(inst)
        #------------------ returnToQueriersLocationWithReply( querier , reply )
   
   
def getPlotterType( form ): 
    """
        @param form : Form with whom this programm was called.
    
        @return : Returns the plotter type.
         
    """   
    
    #---------------------------------------------------------------------- try:
    if (  form["preDeterminedSpan"] == _("daily") ) : 
        plotter = "gnuplot"
    else:
        try:
            if int( form["span"] )<= 36 :
                plotter = "gnuplot"
            else:
                plotter = "rrd"        
        except:        
            plotter = "rrd"    
                
        #------------------------------------------------------------------- except:
        #---------------------------------------------------------- plotter = ""
        
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
    #print form
    for key in form.keys():
     #   print key
        value = form.getvalue(key, "")
        if isinstance(value, list):
            # Multiple username fields specified
            newvalue = ",".join(value)
        else:
            newvalue = value
        
        newForm[key.replace("?","")]= newvalue
    
    for param in EXPECTED_PARAMETERS:
        if param not in  newForm.keys():
            newForm[param]   = ''
            
              
    form = newForm
    
    #print form 
           
    return  form



def getLanguage( form ):
    """
        @summary : Returns the language in which 
                   the page should be generated.
        
        @param form: Form containing hte parameters 
                     with whom this program was
                     called.
    
    """
    
    language = ""
    
    try :
        language = form["lang"]
        
    except:
        pass
    
    return language      


     
def  setGlobalLanguageParameters( language ):
    """
        @summary : Sets up all the needed global language 
                   variables so that they can be used 
                   everywhere in this program.
        
        
        @param language: language with whom this 
                         script was called.
     
        @return: None
        
    """
    
    global _ 

    _ = LanguageTools.getTranslatorForModule( CURRENT_MODULE_ABS_PATH, language)    
     
     
 
def main():
    """
        @summary: Based on the plotter specified in the received form,
                  executes query using a broker that's specific to 
                  the said plotter.
    """
    
       
    
    try:              
        
        form = getForm()
        
        language = getLanguage( form )
        
        
        if language == "" : # unspecified language.
            
            querier = getQuerierLocation( form )
            reply = "images=;error=" + _("Error in query broker. Cannot proceed with query. No language was specified.")
            returnToQueriersLocationWithReply( querier, reply )
        
        elif language not in LanguageTools.getSupportedLanguages(): # unsupported language
            
            querier = getQuerierLocation( form )
            reply = "images=;error=" + _("Error in query broker. Cannot proceed with query. %s is not a supported language.") %language
            returnToQueriersLocationWithReply( querier, reply )
                       
        else: #params seem ok
            
            setGlobalLanguageParameters( language  )
            handlePlotRequest(form)
    
    except Exception, instance :   #temp file helpfull for debugging!
        fileHandle= open('graphicsRequestBrokerDebuggingOutput','w')
        fileHandle.write( str(instance) )
        fileHandle.close()
        
        
if __name__ == '__main__':
    main()