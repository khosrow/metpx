#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.


##############################################################################
##
##
## @Name   : generateImageWebPage.py 
##
##
## @author:  Nicholas Lemay
##
## @since: 22-11-2006, last update on :
##
##
## Description : Generates a web pages that gives access to user 
##               to the daily graphics of the last 7 days for all rx sources 
##               and tx clients.
##
##
##############################################################################
"""


"""
    Small function that adds pxlib to the environment path.  
"""
import os, time, sys
sys.path.insert(1, sys.path[0] + '/../../')
sys.path.insert(2, sys.path[0] + '/../../..')


try:
    pxlib = os.path.normpath( os.environ['PXROOT'] ) + '/lib/'
except KeyError:
    pxlib = '/apps/px/lib/'
    
    
import cgi, os, time, sys
import cgitb; cgitb.enable()
from pxStats.lib.StatsPaths import StatsPaths


def returnReplyToQuerier(error =""):
    """
        @summary : Prints an empty reply so that the receiving web page will
                   not modify it's display.
        
    """
    
    if error == "":
        reply = "images='';error='';action=showImageWindow" 
    else:
        reply = "images='';error=%s" %error 
    
    print """
        HTTP/1.0 200 OK
        Server: NCSA/1.0a6
        Content-type: text/plain

    """
    
    print """%s"""  %( reply )



def generateWebPage( images ):
    """
        @summary : Generates a web page that simply displays a
                   series of images one on top of the other.
        
        @param images : List of images to display.           
    
    """
    
    smallImageWidth  = 900
    smallImageHeight = 320
    
    file = StatsPaths.STATSWEBPAGESHTML + "combinedImageWebPage.html"
    fileHandle = open( file, "w")           
    
    
    fileHandle.write( """
    
    <html>
        <head>
        
            <style type="text/css">      
                 a.photosLink{
                
                    display: block;
                
                    width: 1200px;
                
                    height: 310px;
                
                    background: url("") 0 0 no-repeat;
                
                    text-decoration: none;

                }  
                
            </style>    
                  
            <script type="text/javascript" src="../scripts/js/windowfiles/dhtmlwindow.js">

                This is left here to give credit to the original
                creators of the dhtml script used for the group pop ups:
                /***********************************************
                * DHTML Window Widget-  Dynamic Drive (www.dynamicdrive.com)
                * This notice must stay intact for legal use.
                * Visit http://www.dynamicdrive.com/ for full source code
                ***********************************************/

            </script>

            <script>
                counter =0;
                function wopen(url, name, w, h){
                // This function was taken on www.boutell.com

                    w += 32;
                    h += 96;
                    counter +=1;
                    var win = window.open(url,
                    counter,
                    'width=' + w + ', height=' + h + ', ' +
                    'location=no, menubar=no, ' +
                    'status=no, toolbar=no, scrollbars=no, resizable=no');
                    win.resizeTo(w, h);
                    win.focus();
                }
                
                function transport( image ){
                    wopen( image, 'popup', %s, %s);
                
                }
                
            </script>
               
        </head>
        <body>
        
    """ %( smallImageWidth, smallImageHeight ) )
    
    

    
    for i in range(len(images) ):
    
        fileHandle.write(""" 
            <a href="#" class="photosLink"  name="photo%s" onclick="javascript:transport('%s')" id="photo%s" border=0>
            </a>
            <script>
                document.getElementById('photo%s').style.background="url(" + "%s" + ") no-repeat";
            </script>
            
        """%( i, images[i], i, i, images[i] ) )
    
    
    
    
    fileHandle.write( """    
    
        </body>
    </html>
    
    """)
    
    
    fileHandle.close()
    
    os.chmod(file,0777)

    
def getImagesFromForm():
    """
        @summary : Parses form with whom this program was called.
        
        @return: Returns the images foud within the form.
        
    """
    
    images = []
    
    newForm = {}
    
    form = cgi.FieldStorage()

    for key in form.keys():
        value = form.getvalue(key, "")
        print value
        if isinstance(value, list):
            newvalue = ",".join(value)
                   
        else:
            newvalue = value
        
        newForm[key.replace("?","")]= newvalue    

    try:
        images = newForm["images"]  
        print images 
        images = images.split(';')
        print images 
    except:
        pass
        
    return images 


def main():
    """
        @summary : Generate an html page displaying all the image received in parameter. 
                   Replies to the querier after generating web page so that querier
                   is informed the page was generated.     
    """
   
    images = getImagesFromForm()
    #print images
    generateWebPage( images )
    returnReplyToQuerier()


        
        
if __name__ == '__main__':
    main()   
    

    
    