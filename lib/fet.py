#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#
#  File Exchange Tracker
#	(aka, PDS ++ )
#
#  flow:
#	-- open directory, read name, create DB entry, link DB entry to client dirs.
#          do the above in a manner compatible with PDS.
#
#       -- if we do the delivery thing, then base it on curl (pycurl?) robust
#          functionality for Command line URL's does get & put with retries.
#
#
#  Inputs:
#		-- ingest directory       ingestdir
#		-- client configurations  clientconfigs
#
# 2005/01/10 - begun by Peter Silva
#

import re
import fnmatch
import copy
import os
import time
import string
import sys
import signal
import log

#FET_DATA='/apps/px/'
#FET_DATA='/tmp/fet/'
FET_DATA='/apps/px/'
FET_DB= 'db/today/' 

FET_TX= 'tx/'
FET_RX= 'rx/'

FET_ETC='/apps/px/etc/'
#FET_ETC='../etc/'

#
# These URL routines are extremely stupid.
#    -- there is a module called urlparse, which does most of the same job.
#       FIXME: these routine should #1 be separated into another module, and:
#              #2 use python urlparse and just do the rest.
#              could reduce size of routines considerably

def urlSplit(url):

  protocol=''
  host=''
  port=''
  user=''
  password=''
  dirspec=''

  delim = url.find(':')
  protocol = url[0:delim]
  if protocol == 'file':
    rest = url[delim+1:]
  else:
    rest = url[delim+3:]

#  print 'urlSplit begin, url: ', url, ' rest: ', rest

  if rest[0] == '/':
    destdir = rest
  else:
    delim = string.find(rest,'/')
    if delim > 0:
       dirspec= rest[delim:]
       rest = rest[0:delim]
    else:
       dirspec=''
       
    delim = string.find(rest,'@')
    if delim > 0 :
      host = rest[delim+1:]
      rest = rest[0:delim]
      delim = string.find(host, ':' )
      if delim > 0:
        port = host[delim+1:]
        host = host[0:delim]

      delim = string.find(rest, ':')
      if delim > 0 :
        user = rest[:delim]
        password = rest[delim+1:]
      else:
        user=rest
    else:
      host=rest

#  print "urlSplit proto="+ protocol +" dir="+ dirspec +' u='+ user +' pw='+ password +' h='+ host  +' port='+ port 
  return [ protocol, dirspec, user, password, host, port ]


def urlJoin( protocol, destdir, user, pw, host, port ):

#  print "urlJoin proto="+ protocol +" dir="+ destdir +' u='+ user +' pw='+ pw +' h='+ host  +' p='+ port 
  if protocol == 'file':
     it = protocol + ':'
  else:
    it = protocol + '://'
    if user != '':
      it = it + user 
      if pw != '':
        it = it + ':' + pw
      it = it + '@'
    it = it + host

    if port != '':
      it = it + ':' + port

  if destdir != '':
    if destdir[0] != '/':
       it = it + '/'
    it = it + destdir
   
#  print "urlJoin it=", it
  return it


def lockStopOrDie(lfn, cmd):

  createDir( os.path.dirname(lfn) )
  if os.path.exists( lfn ):
    lockfile = open( lfn , 'r' )
    lockpid = int(lockfile.read())
    lockfile.close()
    if cmd == 'stop':
      try:
        os.kill(lockpid,signal.SIGTERM)
      except:
        pass
      os.unlink( lfn )
      sys.exit(0)
    else:
      print "FATAL: queue locked by process: " + repr(lockpid)
      sys.exit(1)

  lockfile = open( lfn , 'w' )
  lockfile.write( repr(os.getpid()) )
  lockfile.close()



#
# config reader
#



"""
  fills global 'patterns' list of the form:

  clients is a keyed data structure... 
      filled with list values of the form:
  [ [ patterns, default_dest, ftp_timer, q_timer, time_window, sleep_timer, debug_level, chmod ], ... ]

"""
clients = {}

# 
# FIXME: This isn't done right, there should be a parent class
#        with inheritance to override it.  but this is just a skeleton.
#
# -- for a file sender
clientdefaults = [ [], '','10','3600','3600','10','3','000'  ]
#
# for AM sender
clientdefaults = [ [], '','','','','','',''  ]


# FIXME: currently get one global list of clients.
#        if it were structured such that all the patterns were per client
#        indices, then it could break out faster on first match.
#

def readClients(logger):
  """ read the client configuration directory 

  this provides all the information necessary for routing files to 
  their tx queues and the information needed for file transmission.
  """
  global clients
  global clientdefaults

  clients = {}

  for cfname in os.listdir( FET_ETC + FET_TX ):
    if cfname[-5:] != '.conf':
       continue
    cliconf = open( FET_ETC + FET_TX + cfname, 'r' )
    clientid = cfname[:-5]
    isactive=0
    mask=cliconf.readline()
    destdir=''
    client=clientdefaults
    patterns = []
    protocol = 'ftp'
    user=''
    password=''
    host=''
    port=''
    destdir=''
    destfn=''
    while mask :
      maskline = mask.split()
      if ( len(maskline) >= 2 and not re.compile('^[ \t]*#').search(mask) ) :
        if maskline[0] == 'imask' :
	  destination=urlJoin(protocol,destdir,user,password,host,port)
          #print "destination: ", destination
	  patterns = patterns + [ maskline + [ destination, destfn ] ]
        elif maskline[0] == 'active':
	    if maskline[1] == 'yes':
	       isactive=1 
        elif maskline[0] == 'emask':
	    patterns = patterns + [ maskline ]
        elif maskline[0] == 'directory':
	  destdir = maskline[1]
        elif maskline[0] == 'destination':
	  ( protocol, dirspec, uspec, pwspec, hspec, pspec ) = \
	  	urlSplit( maskline[1] )
	  if len(maskline) > 2 :
	     destfn = maskline[2]
          if dirspec != '':
	     destdir = dirspec
          if uspec != '':
	     user = uspec
          if pwspec != '':
	     password = pwspec
          if hspec != '':
	     host = hspec
          if pspec != '':
	     port = pspec
	  if client[1] == '':
	     client[1]=urlJoin(protocol,destdir,user,password,host,port)

#          print "after urlSplit proto="+ protocol +" destdir="+ destdir +' u='+ user +' pw='+ password +' h='+ host  +' port='+ port 
        elif maskline[0] == 'host':
	  host = maskline[1]
        elif maskline[0] == 'user':
	  user = maskline[1]
        elif maskline[0] == 'filename':
	  destfn = maskline[1]
        elif maskline[0] == 'password':
	  password = maskline[1]
        elif maskline[0] == 'protocol':
	  protocol = maskline[1]
        elif maskline[0] == 'ftp_timer':
	  client[2] = maskline[1]
        elif maskline[0] == 'queue_timer':
	  client[3] = maskline[1]
        elif maskline[0] == 'time_window':
	  client[4] = maskline[1]
        elif maskline[0] == 'sleep_timer':
	  client[5] = maskline[1]
        elif maskline[0] == 'debug_level':
	  client[6] = maskline[1]
        elif maskline[0] == 'chmod':
	  client[7] = maskline[1]
	mask=cliconf.readline()

    cliconf.close()
    client[0] = patterns
    if isactive == 1:
      clients[clientid] = copy.deepcopy(client)
      logger.writeLog( logger.INFO, "read config of client " + clientid )
      isactive=0
    else:
      logger.writeLog( logger.INFO, "ignored config of client " + clientid )
    
  # dump clients db
#  for k in clients.keys():
#     print "client ", k, " is: ",  clients[k], "\n"

  #print "\n\n\nPatterns\n\n\n"
  #print patterns



sources = {}
"""

  each source is a list of the form:
  [ priority, system, site, type, format, ingester ]

"""
sourcedefaults = [ '', '', '', '', '', '' ]

def readSources(logger):
  """ read the source configuration directory for settings
  """
  global sources
  global sourcedefaults

  sources = {}

  #print "readSources"
  for cfname in os.listdir( FET_ETC + FET_RX ):
    if cfname[-5:] != '.conf':
       continue
    sourceid = cfname[:-5]
    srcconf = open( FET_ETC + FET_RX + cfname, 'r' )
    isactive=0
    source = sourcedefaults
    src=srcconf.readline()
    while src :
      srcline=src.split()
      if ( len(srcline) >= 2 and not re.compile('^[ \t]*#').search(src) ) :
        if srcline[0] == 'priority':
	  source[0]  = int(srcline[1])
        elif srcline[0] == 'active':
	    if srcline[1] == 'yes':
	       isactive=1 
        elif srcline[0] == 'system':
	  source[1]  = srcline[1]
        elif srcline[0] == 'site':
	  source[2]  = srcline[1]
        elif srcline[0] == 'type':
	  source[3]  = srcline[1]
        elif srcline[0] == 'format':
	  source[4]  = srcline[1]
        elif srcline[0] == 'ingester':
	  source[5]  = srcline[1:]
      src=srcconf.readline()

    srcconf.close()

    if isactive == 1:
      sources[sourceid] = copy.deepcopy(source)
      logger.writeLog( logger.INFO, "read config of source " + sourceid )
    else:
      logger.writeLog( logger.INFO, "ignored config of source " + sourceid )

    #print "sources are: ", sources

def sourceQDirName(s):
  return FET_DATA + FET_RX + s

def ingestName(r,s):
  """ map reception to ingest name, based on the source configuration.

      used to be called: sourceRx2Ingestname(r,s):
      This just inserts missing fields,  like whattopds.  DUMB!
      FIXME: have a library of functions, configurable per client, to
         perform the mapping, perhaps using rmasks ? & other args.
  """
  rs = r.split(':')
  if ( len(rs) == 1 ) or sources[s][1] == '' :
     rs = rs + [ sources[s][1] ]
  if len(rs) == 2 or sources[s][2] == '' :
     rs = rs + [ sources[s][2] ]
  if len(rs) == 3 or sources[s][3] == '' :
     rs = rs + [ sources[s][3] ]
  if len(rs) == 4 or sources[s][4] == '' :
     rs = rs + [ sources[s][4] ]
  if len(rs) == 5 or sources[s][5] == '' :
     rs = rs + [ repr(sources[s][0]) ]
  rs = rs + [ time.strftime( "%Y%m%d%H%M%S", time.gmtime(time.time()) ) ]
     
  return string.join(rs,':')


def dbName(ingestname):
  """ given an ingest name, return an relative database name

  given a file name of the form:
      what : ori_system : ori_site : type : format :
  link it to 
      db/<today>/type/ori_system/ori_site/ingestname
  (same pattern as PDS)
  path is relative to FET_DATA (includes db)

  NB: see notes/tests.txt for why the date/time is recalculated everytime.
  """
  if ingestname.count(':') >= 4 :
    dirs = ingestname.split(':')
    today = time.strftime( "%Y%m%d/", time.gmtime(time.time()) )
    return FET_DATA + 'db/' + today + dirs[3] + '/' + dirs[1] + '/' + dirs[2] + '/' + ingestname 
  else:
    return ''


def clientQDirName( client, pri ):
  """ return the directory into which a file of a given priority should be placed.
  A couple of different layouts being contemplated.
  /apps/px/tx/<client>/1_YYmmddhh ??
  """
  global clients
  return FET_DATA + FET_TX + client + '/' + pri + '_' \
             + time.strftime( "%Y%m%d%H", time.gmtime(time.time()) ) + '/'


def clientMatch(c,ingestname):

  for p in clients[c][0]:
    if fnmatch.fnmatch(ingestname,p[1]) :
      if p[0] == 'imask':
	 return p
  return []


def clientMatches(ingestname):
  """ returns a list of clients to whome the file with ingestname should be sent.

   match ingestname against global list of client patterns.

   return a list of clients which should 
	[ [ client, host, dir ], [ client, host, dir ], ... ]
  """

  global clients

  hits=[]

#  print "client matches for " + ingestname 
  for c in clients.keys():
    p = clientMatch(c,ingestname)
    if p != []:
      hits = hits + [ [ c ] + p ]

#  print hits
  return hits



def destFileName(ingestname, climatch):
  """ return the appropriate destination give the climatch client specification.

  return the appropriate destination file name for a given client match from patterns.

  DESTFN=fname -- change the destination file name to fname
  WHATFN       -- change the file name
  NONE	       -- use the entire ingest name, except... 
  TIME or TIME:   -- TIME stamp appended  
  TIME:RASTER:COMPRESS:GZIP -- modifiers... hmm... (forget for now...)
  SENDER	-- SENDER=

  FIXME: unknowns:
    SENDER not implemented
    is DESTFN:TIME allowed? reversing order
    does one add <thismachine> after TIME ?
    INFO Jul 22 17:00:01: /apps/pds//bin//pdsftpxfer: INFO: File SACN59_CWAO_221600_RRB_208967:AMTCP2FILE-EXT:PDS1-DEV:BULLETIN:ASCII::20040722164923:pds1-dev   sent to ppp1.cmc.ec.gc.ca as    SACN59_CWAO_221600_RRB_208967    Bytes= 75
    pdschkprod-bulletin-francais.20050109:INFO Jan 09 16:09:15: pdschkprod 1887: Written 3867 bytes: /apps/pds/pdsdb/BULLETIN/tornade/CMQ/ACC-FP55WG7409160137:tornade:CMQ:BULLETIN:ASCII:SENDER=ACC-FP55WG7409160137X.TXT:20050109160915
    pdschkprod-bulletin-francais.20050109:INFO Jan 09 16:13:39: pdschkprod 1887: Written 4972 bytes: /apps/pds/pdsdb/BULLETIN/tornade/CMQ/ACC-FP54XK7309160151:tornade:CMQ:BULLETIN:ASCII:SENDER=ACC-FP54XK7309160151X.TXT:20050109161339
    p
    What do the RASTER etc... options do? just add suffix?
  
  """

# print "climatch: ", climatch
  specs=climatch[3].split(':')  
#  print 'climatch[4] is +' + climatch[4] + '+'
  dname=ingestname.split(':')[0]
  time_suffix=''

  for spec in specs:
    if spec == 'TIME':
      time_suffix= ':' + time.strftime( "%Y%m%d%H%M%S", time.gmtime(time.time()) )
    elif (spec == 'WHATFN') or (spec == ''):  # blank results from "TIME" alone as spec
      dfn=dname
    elif spec == 'NONE':
      dfn=ingestname 
    elif re.compile('DESTFN=.*').match(spec):  
      dfn=spec[7:]
    elif (spec[0:4] == 'RASTER') or (spec[0:4] == 'COMPR' ):
      dfn= dname + ':' + spec
    elif spec[0] == '/':
      dfn= spec[4] + '/' + dname # local directory name
    elif spec == 'SENDER':
      dfn= (dname[5].split('='))[1]
    else:
     print 'ERROR: do not understand destfn parameter: ', climatch
     return ''

  return dfn + time_suffix

"""avoid onerous repeated calls to os.path.exists, by short-circuiting after
   first check.

   FIXME: cleaning out dirs_created? might get big after a while.
      cleaned out in initDB.
"""
dirs_created = []

def createDir(dir):
   """ create a directory if it does not exist

   should I check for rollover?
   """
   global dirs_created

   #print "createDir(", dir, ")"
   if not (dir in dirs_created) and not os.path.exists( dir ):
      os.makedirs( dir, 01775 )
      #print "createDir(", dir, ")"
   dirs_created = dirs_created + [ dir ]


def linkFile(f,l):
  """ make a link l to the existing file f, 
  """
  createDir( os.path.dirname(l) )
#  print "link(", f, l, ")"
  os.link( f, l )


def directIngest(ingestname,clist,pri,lfn,logger):
   """ link lfn into the db & client spools based on ingestname & clients 

       accepts a list of matching clients.
   """

   dbn=dbName(ingestname)
   if ( dbn == '' ):
      return 0

   linkFile(lfn, dbn)
   logger.writeLog( logger.INFO, "linking " + dbn + " to: " + lfn )

   if len (clist) < 1:
     return 1

   for c in clist:
     cname=clientQDirName( c, pri )
     linkFile(dbn , cname + ingestname )   
     logger.writeLog( logger.INFO, "linking for " + c )

   return 1



def ingest(ingestname,lfn,logger):
   """ link lfn into the database & client spools, based on ingestname & pri

      apply all the masks to ingestname to find the clients who should receive
      it, and insert it in their queues.

   """
   pri=ingestname.split(':')[5]
   clist=map( lambda x: x[0], clientMatches(ingestname))
   directIngest(ingestname,clist,pri,lfn,logger)


def initDB(logger):
   """
   initialize the base of the FET spooling tree, rotating the today link
   if needed.  
   
   FIXME: Are there race conditions because of db rollover. ?
        -- added explicit creation based on current time to dbName,
	   so that it doesn't depend on system wide db rollover process.

   so nothing below matters, because nobody uses 'today'.  it is only sugar for humans.

   N.B. There are potential race conditions if multiple ingestors run.
   really, ingest process should be quiescent when the symlink changes.
   	-- both look at the directories and try to roll over at once.
	-- both try to move the symbolic link at a rollover time.
	-- Others try to reference 'today' while it doesn't exist.
	   most built-in processes should use the real directory.
        -- really, only writers to db should be the ingestors.

   Checking a lock every time would be horridly expensive for a once 
   a day event. so they only place this should be called is from somewhere
   that knows the db is quiescent.

   a lock for only the initDB routing would solve most (except 'today' reference)

   FIXME: -- creation of yesterday link doesn't happen if today is missing.
	  -- no logging of this important event, hmm...
   """
   global dirs_created
   global FET_DB

   logger.writeLog( logger.INFO, "dbinit start")
   dirs_created = []
   createDir( FET_DATA + '/.' )
   createDir( FET_DATA + FET_RX )
   createDir( FET_DATA + FET_TX )
   createDir( FET_DATA + "db" )
   todaylink = time.strftime( "%Y%m%d", time.gmtime(time.time()))
   FET_DB = "db/" + todaylink + "/"
   createDir( FET_DATA + FET_DB )
   tl = FET_DATA + "db/today"
   yl = FET_DATA + "db/yesterday"
   if os.path.exists( tl ):
     lnk = os.readlink( tl )
     if ( todaylink != lnk ):
       os.unlink( tl )
       os.symlink( todaylink, tl )
       if os.path.exists( yl ):
         os.unlink( yl )
         os.symlink( lnk, yl )
       
   else:
     os.symlink( todaylink, tl )
     if os.path.exists( yl ):
         os.unlink( yl )
   
   logger.writeLog( logger.INFO, "dbinit done")


def startup(dataDir, configDir, logger):
   global FET_DATA
   global FET_ETC

   FET_DATA=dataDir
   if FET_DATA[-1] != '/':
     FET_DATA = FET_DATA + '/'

   FET_ETC=configDir
   if FET_ETC[-1] != '/':
     FET_ETC = FET_ETC + '/'

   initDB(logger)
   readClients(logger)
   readSources(logger)


# module initialization code
#startup()
