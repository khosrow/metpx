"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: ConfigReader.py
#
# Authors: Daniel Lemay
#
# Date: 2007-03-05
#
# Description: Used to parse cir's configuration file 
#
#############################################################################################
"""

import re, sys
import ColumboPaths

class ConfigReader(object):
    def __init__(self):
        self.configFilename = ColumboPaths.FULL_CIR_CONF
        self.groups = {}
        self.read()

    def read(self):
        try:
            file = open(self.configFilename, 'r')
        except:
            (type, value, tb) = sys.exc_info()
            print ('Type: %s, Value: %s' % (type, value))
            return

        for line in file.readlines():
            if not re.compile('^[ \t]*#').search(line):    
                #print line.strip()
                tag, system, machines, ccs_up, cir_up, cs_up = line.split()
                #print tag, system, machines, ccs_up, cir_up, cs_up
                self.groups[tag] = system, machines.split(','), ccs_up.split(':'), cir_up.split(':'), cs_up.split(':')

        file.close()

    def printInfos(self):
        spacer1 = max([len(key) for key in self.groups.keys()])
        spacer2 = 8

        spacer3 = 0
        spacer4 = 0
        spacer5 = 0
        spacer6 = 0

        for key in self.groups.keys():
            l = len(str(self.groups[key][1]))
            m = len(str(self.groups[key][2]))
            n = len(str(self.groups[key][3]))
            o = len(str(self.groups[key][4]))
            if l > spacer3: spacer3 = l
            if m > spacer4: spacer4 = m
            if n > spacer5: spacer5 = n
            if o > spacer6: spacer6 = o
            
        header = "tag%ssystem%sccs machines%sccs_user:passwd%scir_user:passwd%scs_user:passwd" % ((spacer1+2-len('tag'))* ' ', (spacer2+2-len('system'))* ' ',
                                                                          (spacer3+2-len('ccs machines'))* ' ', (spacer4+2-len('ccs_user:passwd'))* ' ', 
                                                                          (spacer5+2-len('cir_user:passwd'))* ' ')
        print (len(header)+ spacer6 - len('cs_user:passwd')) * "#" 
        print header
        print (len(header)+ spacer6 - len('cs_user:passwd')) * "#" 

        for key in self.groups.keys():
            print "%s%s%s%s%s%s%s%s%s%s%s" % (key, (spacer1-len(key) + 2) * ' ', 
                                             self.groups[key][0], (spacer2-len(str(self.groups[key][0])) + 2) * ' ', 
                                             self.groups[key][1], (spacer3-len(str(self.groups[key][1])) + 2) * ' ', 
                                             self.groups[key][2], (spacer4-len(str(self.groups[key][2])) + 2) * ' ', 
                                             self.groups[key][3], (spacer5-len(str(self.groups[key][3])) + 2) * ' ', 
                                             self.groups[key][4])        

if __name__ == '__main__':
    cr = ConfigReader()
    cr.printInfos()
