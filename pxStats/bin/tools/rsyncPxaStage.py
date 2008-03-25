#! /usr/bin/env python
import commands

def main():
    print "rsync -avzr --delete-before -e ssh pds@pxa1-stage:/apps/px/log/   /apps/px/pxStats/data/logFiles/pxa1-stage/"
    status,output = commands.getstatusoutput("rsync -avzr --delete-before -e ssh pds@pxa1-stage:/apps/px/log/   /apps/px/pxStats/data/logFiles/pxa1-stage/")
    print status,output
    
    print "rsync -avzr --delete-before -e ssh pds@pxa2-stage:/apps/px/log/   /apps/px/pxStats/data/logFiles/pxa2-stage/"
    status,output = commands.getstatusoutput("rsync -avzr --delete-before -e ssh pds@pxa2-stage:/apps/px/log/   /apps/px/pxStats/data/logFiles/pxa2-stage/")
    print status,output
    

    
    
if __name__ == '__main__':
    main()