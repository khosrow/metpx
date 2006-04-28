var timer = 76;
var imgDir = "/images/";
var color = 'bluec';
var started = 1;
var maxStoppedTime = 600; // in seconds
var stoppedTime = 0;   

function toggleState() {

    if (started == 1) {
        started = 0;
        color = 'redc';
    }
    else {
        started = 1;
        color = 'bluec';
    }
}

function getTime() {

   //color = 'bluec';

   redc1 = new Image(); redc1.src = "/images/red1c.gif";
   redc2 = new Image(); redc2.src = "/images/red2c.gif";
   redc3 = new Image(); redc3.src = "/images/red3c.gif";
   redc4 = new Image(); redc4.src = "/images/red4c.gif";
   redc5 = new Image(); redc5.src = "/images/red5c.gif";
   redc6 = new Image(); redc6.src = "/images/red6c.gif";
   redc7 = new Image(); redc7.src = "/images/red7c.gif";
   redc8 = new Image(); redc8.src = "/images/red8c.gif";
   redc9 = new Image(); redc9.src = "/images/red9c.gif";
   redc0 = new Image(); redc0.src = "/images/red0c.gif";
   redCc = new Image(); redCc.src = "/images/redCc.gif";

   bluec1 = new Image(); bluec1.src = "/images/bluec1.gif";
   bluec2 = new Image(); bluec2.src = "/images/bluec2.gif";
   bluec3 = new Image(); bluec3.src = "/images/bluec3.gif";
   bluec4 = new Image(); bluec4.src = "/images/bluec4.gif";
   bluec5 = new Image(); bluec5.src = "/images/bluec5.gif";
   bluec6 = new Image(); bluec6.src = "/images/bluec6.gif";
   bluec7 = new Image(); bluec7.src = "/images/bluec7.gif";
   bluec8 = new Image(); bluec8.src = "/images/bluec8.gif";
   bluec9 = new Image(); bluec9.src = "/images/bluec9.gif";
   bluec0 = new Image(); bluec0.src = "/images/bluec0.gif";
   //bluecb = new Image(); bluecb.src = "/images/bluecb.gif";


   if (started == 1) {
      timer--;
   }
   else {
      if (stoppedTime <= maxStoppedTime) {
         stoppedTime++;
      }
      else {
         started = 1;
         color = 'bluec';
         stoppedTime = 0;
      }
   }

   if (timer == -1) {
      location.href = location.href;
   }
   else {
      if (timer <= 9 && timer) {
         document.images.dizaines.src = eval(color + "0.src");
         document.images.unites.src = eval(color + timer + ".src");
      }
      else {
         document.images.dizaines.src = eval(color + Math.floor(timer/10) + ".src");
         document.images.unites.src = eval(color + (timer%10) + ".src");
      }
   }
   setTimeout("getTime();", 1000);
}
