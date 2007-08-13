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

sys.path.insert(1, sys.path[0] + '/../../')
sys.path.insert(2, sys.path[0] + '/../../..')
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.StatsPaths import StatsPaths

LOCAL_MACHINE = os.uname()[1]



def generateWebPage( sourlientNames, outputFileName):
    """
        @summary: Generates popupAdder web page named after the 
                  received outputFileName and based on the 
                  list of sourlients names received  
        
    """
    
    if not  os.path.isdir( os.path.dirname(outputFileName) ):
        os.makedirs( os.path.dirname(outputFileName) )
    
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
    
        <script type="text/javascript" language="JavaScript">
            
            function popupAddingWindow( url ) {
                var newWindow;
                var props = 'scrollBars=no,resizable=no,toolbar=no,menubar=no,location=no,directories=no,width=700,height=300';
                newWindow = window.open(url, "Add_from_Src_to_Dest", props);
            }
            
            function closeWindow(){
                window.close();
            }
            
            // Fill the selcted item list with the items already present in parent.
            function copyLists( srcList, destList ) {
                
                var len = destList.length;
                for(var i = 0; i < srcList.length; i++) {
                    if ( srcList.options[i] != null ) {
                        
                        //Check if this value already exist in the destList or not
                        //if not then add it otherwise do not add it.
                        var found = false;
                        for(var count = 0; count < len; count++) {
                            if (destList.options[count] != null) {
                                if (srcList.options[i].text == destList.options[count].text) {
                                    found = true;
                                    break;
                                }
                            }
                        }
                        
                        if (found != true) {
                            destList.options[len] = new Option(srcList.options[i].text); 
                            len++;
                        }
                    }
                }
            }
            
            
            // Add the SELECTED items from the source to destination list
            // will only add the items wich are not allready present in dest list.
            function addSrcToDestList( srcList, destList ) {
                var len = destList.length;
                for(var i = 0; i < srcList.length; i++) {
                    if ((srcList.options[i] != null) && (srcList.options[i].selected)) {
                        //Check if this value already exist in the destList or not
                        //if not then add it otherwise do not add it.
                        var found = false;
                        for(var count = 0; count < len; count++) {
                            if (destList.options[count] != null) {
                                if (srcList.options[i].text == destList.options[count].text) {
                                    found = true;
                                    break;
                                }
                            }
                        }
                        if (found != true) {
                            destList.options[len] = new Option(srcList.options[i].text); 
                            len++;
                        }
                    }
                }
            }
            
            // Deletes from the destination list.
            function deleteFromList( list ) {
                var len = list.options.length;
                for(var i = (len-1); i >= 0; i--) {
                    if ((list.options[i] != null) && (list.options[i].selected == true)) {
                        list.options[i] = null;
                    }
                }
            }
            
        
        </script>
      
      </head>
      
        <body text="#FFFFFF" link="#FFFFFF" vlink="000000" bgcolor="#CCCCCC">
            <center>
            
            <form name="adderForm" method="POST">
                
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
                            <input type="button" value="Done" onClick ="javascript:window.opener.copyLists(document.forms['adderForm'].elements['destList'], window.opener.document.forms['inputForm'].elements['sourlientList']);javascript:closeWindow();">
                        </td>
                    </tr>
                
                </table>
            
            </form>
    
        
        </body>
    
    </html>
    
    """
    
    fileHandle.close()                 
    sys.stdout = oldStdOut #resets standard output 
    

def returnReply( error = '' ):
    """
        @summary : Prints an empty reply so that the receiving web page will
                   not modify it's display.
        
    """
    
    reply = "images='';error=%s" %error 
    
    print """
        HTTP/1.0 200 OK
        Server: NCSA/1.0a6
        Content-type: text/plain

    """
    
    print """%s"""  %( reply )    


    
def main():
    """
        Generates the web page based on the received 
        machines and file type parameters.
        
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
        machines  = form['machines']
        machine = machines.split( ',' )[0]
        machines = machines.replace( ',', '' )
    except:
        error = "Error. Machine names need to be specified."
        machine = ""
    
    if machines != "":          
        
        rxNames, txNames = GeneralStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, machine )
    
    if fileType == "tx":
        generateWebPage(txNames, "../../html/popUps/%s%sPopUpSourlientAdder.html" %( fileType, machines ) )
    elif fileType == "rx":
        generateWebPage(rxNames, "../../html/popUps/%s%sPopUpSourlientAdder.html" %( fileType, machines ) )
    
    returnReply('') 
        
if __name__ == '__main__':
    main()
