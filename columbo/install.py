#!/usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""
"""
#############################################################################################
# Name: install.py
#
# Author: Daniel Lemay
#
# Date: 2005-08-02
#
# CCS = Columbo Crime Scene (Each Individual PDS is a crime scene)
# CIR = Columbo Investigation Room (Investigation Room is on a LVS, clues are merged in results)
# CS  = Columbo Show (The Show is on a LVS)
#
# Description: Installation program
#
# TODO: - Be able to create what root have to create (/web, /etc/sudoers)??
#       - Verify if what root have to create exists? Maybe parse the /etc/sudoers to see if it is correct?
#       - Create ssh keys for PDS user??
#
#############################################################################################
"""
import os, sys, shutil, commands, getopt
sys.path.append(sys.path[0] + '/lib')

from ColumboPath import *

TYPE = None

def usage():
    print "\nUsage: ./install.py (-t|--type) ('FRONT', 'BACK')\n"
    print "Example 1: ./install.py --type 'BACK' (for a backend  => Columbo Show web server IS NOT ON this machine)"
    print "Example 2: ./install.py -t 'FRONT'    (for a frontend => Columbo Show web server IS ON this machine)\n"

def getOptionsParser():
     global TYPE

     type = False
     try:
         opts, args = getopt.getopt(sys.argv[1:], 't:h', ['help', 'type='])
         #print opts
         #print args
     except getopt.GetoptError:
         # print help information and exit:
         usage()
         sys.exit(2)

     for option, value in opts:
         if option in ('-h', '--help'):
             usage()
             sys.exit()
         if option in ('-t', '--type'):
             type = True
             if value in ['BACK', 'FRONT']:
                 TYPE = value
             else:
                 usage()
                 sys.exit(2)

     # We must specify a type
     if type  is False:
         usage()
         sys.exit()

def makeCCSPaths(type):
    dir = CCS + '/clues'
    if not os.path.exists(dir):
        os.mkdir(dir, 0775)
        print("CCS clues directory (%s) has been CREATED" % dir)

    dir = CCS + '/log'
    if not os.path.exists(dir):
        os.mkdir(dir, 0775)
        print("CCS log directory (%s) has been CREATED" % dir)

    dir = '/apps/pds/bin'
    source = COLUMBO_HOME + '/lib/ToggleSender.columbo'
    if  os.path.exists(dir):
        shutil.copy(source, dir)
        os.chmod(source, 0777)
        print("ToggleSender.columbo copied in %s" % dir)
    else:
        if type == 'BACK':
            print("PROBLEM: ToggleSender.columbo cannot be copied in %s" % dir)
    
def makeCIRPaths():
    dir = CIR + '/clues'
    if not os.path.exists(dir):
        os.mkdir(dir, 0775)
        print("CIR clues directory (%s) has been CREATED" % dir)

    dir = CIR + '/results'
    if not os.path.exists(dir):
        os.mkdir(dir, 0775)
        print("CIR results directory (%s) has been CREATED" % dir)

    dir = CIR + '/log'
    if not os.path.exists(dir):
        os.mkdir(dir, 0775)
        print("CIR log directory (%s) has been CREATED" % dir)
    
    source = CIR_PROG 
    if os.path.isfile(source):
        os.chmod(source, 0755)
        print("%s has been chmod 755" % source) 

def makeCSPaths():
    dir = CS + '/log'
    if not os.path.exists(dir):
        os.mkdir(dir, 0777)
        print("CS log directory (%s) has been CREATED" % dir)
    else:
        os.chmod(dir, 0777)
        print("CS log directory (%s) has been chmod 777 " % dir)

    dir = CS + '/results'
    if not os.path.exists(dir):
        os.mkdir(dir, 0777)
        print("CS results directory (%s) has been CREATED" % dir)
    else:
        os.chmod(dir, 0777)
        print("CS results directory (%s) has been chmod 777" % dir)

    dir = CS + '/graphs'
    if not os.path.exists(dir):
        os.mkdir(dir, 0777)
        print("CS results directory (%s) has been CREATED" % dir)
    else:
        os.chmod(dir, 0777)
        print("CS results directory (%s) has been chmod 777" % dir)

    # Make sure all files are executable
    dir = CS + '/lib'
    files = os.listdir(dir)
    for file in files:
        os.chmod(dir + '/' + file, 0755)
   

# Only on front end (where the web server is)
def makeCGIPaths():

    if not os.path.isdir('/web'):
        print("root must create a /web directory")
        sys.exit(1)

    dir = '/web/columbo'
    if not os.path.exists(dir):
        os.mkdir(dir, 0755)
        print("%s directory has been CREATED" % dir)
        
    #dir = '/web/columbo/log'
    #if not os.path.exists(dir):
    #    os.mkdir(dir, 0775)
    #    print("%s directory has been CREATED" % dir)

    dir = '/web/columbo/cgi-bin'
    if not os.path.exists(dir):
        os.mkdir(dir, 0755)
        print("%s directory has been CREATED" % dir)

    # Now I have to copy all that is under COLUMBO_HOME/web/ to /web/columbo/
    command = "cp -fpr %s/web/* /web/columbo/" % COLUMBO_HOME
    status, output = commands.getstatusoutput(command)
    print("Status of %s is: %s, output = %s" % (command, status, output))

    # Finally, I have to copy CS and lib directories under /web/columbo/cgi-bin
    target = '/web/columbo/cgi-bin/'

    command = "cp -fpr %s %s" % (CS, target)
    status, output = commands.getstatusoutput(command)
    print("Status of %s is: %s, output = %s" % (command, status, output))

    command = "cp -fpr %s %s" % (COLUMBO_HOME + '/lib', target)
    status, output = commands.getstatusoutput(command)
    print("Status of %s is: %s, output = %s" % (command, status, output))

    #command = "ln -s %s %s" % (CS + '/log/PX_Errors.txt', '/web/columbo/log/PX_Errors.txt')
    #status, output = commands.getstatusoutput(command)
    #print("Status of %s is: %s, output = %s" % (command, status, output))

    command = "ln -s %s %s" % (CS + '/graphs/' , '/web/columbo/')
    status, output = commands.getstatusoutput(command)
    print("Status of %s is: %s, output = %s" % (command, status, output))

    command = "ln -s %s %s" % (CS + '/log/' , '/web/columbo/')
    status, output = commands.getstatusoutput(command)
    print("Status of %s is: %s, output = %s" % (command, status, output))

    file  = '/etc/sudoers'
    if os.path.isfile(file):
        print("%s exists, is it correct?" % file)
    else:
        print("PROBLEM: /etc/sudoers doesn't exists")

def main():

    getOptionsParser()
    #print("Type = %s " % TYPE)

    os.umask(0000)
    makeCCSPaths(TYPE)

    # Only if a web server will host Columbo Show
    if TYPE == 'FRONT':
        makeCIRPaths()
        makeCSPaths()
        makeCGIPaths()

if __name__ == '__main__':
    main()
