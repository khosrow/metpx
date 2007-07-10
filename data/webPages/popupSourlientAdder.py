#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.


##############################################################################
##
##
## @Name   : PopSourlientUpAdder.py 
##
##
## @author :  Nicholas Lemay
##
## @since  : 2007-07-03
##
## @summary : This file is to be called from the graphicsResquest page to update
##            the samll popup adder utility windows.   
##
##                   
##
##############################################################################
"""

import cgi, os, time, sys
import cgitb; cgitb.enable()

sys.path.insert(1, sys.path[0] + '/../../../')
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.StatsPaths import StatsPaths

LOCAL_MACHINE = os.uname()[1]

def generateWebPage( sourlientNames, outputFileName):
    """
        @summary: Generates popupAdder web page named after the 
                  received outputFileName and based on the 
                  list of sourlients names received  
        
    """
    
    """ Redirect the output"""
    fileHandle = open( outputFileName, "w" )
    oldStdOut = sys.stdout #save previous stdout
    sys.stdout = fileHandle
    
    print """
    <html>
      <head>
        
        <title>Add items to list.</title>
        <meta name="Author" content="Nicholas Lemay">
        <meta name="Description" content="Small popup window used to add items into a list. To be used with graphicsResquests.py">
        <meta name="Keywords" content="">
        <style type="text/css">
            div.selectObject{
                width:300px;            
                height: auto;
            }
        
        </style>
        <link rel="stylesheet" type="text/css" href="/css/style.css">
    
        <script src="js/popupListAdder.js"></script>
      
      </head>
      
        <body text="#FFFFFF" link="#FFFFFF" vlink="000000" bgcolor="#CCCCCC">
            <center>
            
            <form name=" adderForm" method="POST">
                
                <table bgcolor="#99FF99" >
                    
                    <tr>
                        <font color ="white">
    
                            <td bgcolor="#006699" width="300" >Available</td>
                            <td bgcolor="#006699" >&nbsp;</td>
                            <td bgcolor="#006699" width="300" >Selected</td>
                        </font>    
                    </tr>
                    
                    <tr>
        
                        <td bgcolor="#99FF99" width="300">
                                
                                <select size="12" style="width: 300px;" name="srcList" multiple> 
  
    """
    
    for i in range(len(sourlientNames)):
        print """    
                                    <option value="%s">%s</option>                      
        """%( i+1, sourlientNames[i] )
   
    print """   
                                
                                </select>
    
                        
                        </td>
                        
                        <td bgcolor="#99FF99" width="74" align="center">
                            <input type="button" value=" >> " onClick="javascript:addSrcToDestList( document.forms['adderForm'].elements['srcList'], document.forms['adderForm'].elements['destList']  )">
                            <br><br>
                            <input type="button" value=" << " onclick="javascript:deleteFromList( document.forms['adderForm'].elements['destList'] );">
                        </td>
                        
                        <td bgcolor="#99FF99" width="300">               
                            <select size="12" style="width: 300px;" name="destList" multiple>
                            </select>
    
                        </td>
                    
                    </tr>
                    
                    <tr>
                        <td colspan=3 align="center">
                            <input type="button" value="Done" onClick =" javascript:copyLists(window.document.forms['adderForm'].elements['destList'], self.opener.document.forms['gnuplotForm'].elements['sourlientList']);javascript:closeWindow();">
                        </td>
                    </tr>
                
                </table>
            
            </form>
    
        
        </body>
    
    </html>
    
    """
    
    fileHandle.close()                 
    sys.stdout = oldStdOut #resets standard output 
    
    
    
def main():
    """
        Generates the web page based on the received 
        machine and file type parameters.
        
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
    
    try:
        fileType = form['fileType']
        if fileType !='tx' and fileType != 'rx':
            error= "Error. File type needs to be either rx or tx."
        
    except:
        fileType = ""
        
    try:
        machine  = form['machine']
    except:
        error = "Error. Machine name needs to be specified."
        machine = ""
    
    if machine != "":          
        rxNames, txNames = GeneralStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, machine )
    
    if fileType == "tx":
        generateWebPage(txNames, "%s/%sPopSourlientUpAdder.html" %( StatsPaths.STATSWEBPAGES, fileType ) )
    elif fileType == "rx":
        generateWebPage(rxNames, "%s/%sPopSourlientUpAdder.html" %( StatsPaths.STATSWEBPAGES, fileType ) )
    

if __name__ == '__main__':
    main()
