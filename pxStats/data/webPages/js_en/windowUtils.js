/*
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
*/

var newWindow;
var counter;
counter = 0;

function popIt(url)
{
   newWindow=window.open(url,'PDSErrors', "status=1, toolbar=1, menubar=1, resizable=1, scrollbars=1");

}

function popItGraph(url)
{
   counter += 1;
   newWindow=window.open(url, counter, "dependent=0, status=0, toolbar=0, menubar=0, resizable=1, scrollbars=0, left=190, top=0, width=1280, height=1000");

}


