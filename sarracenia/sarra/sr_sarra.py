#!/usr/bin/python3
#
# This file is part of sarracenia.
# The sarracenia suite is Free and is proudly provided by the Government of Canada
# Copyright (C) Her Majesty The Queen in Right of Canada, Environment Canada, 2008-2015
#
# Questions or bugs report: dps-client@ec.gc.ca
# sarracenia repository: git://git.code.sf.net/p/metpx/git
# Documentation: http://metpx.sourceforge.net/#SarraDocumentation
#
# sr_sarra.py : python3 program allowing users to listen and download product from
#               another sarracenia server or from user posting (sr_post/sr_watch)
#               and reannounce the product on the current server
#
#
# Code contributed by:
#  Michel Grenier - Shared Services Canada
#  Last Changed   : Dec 22 09:20:21 EST 2015
#
########################################################################
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, 
#  but WITHOUT ANY WARRANTY; without even the implied warranty of 
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA
#
#============================================================
# usage example
#
# sr_sarra [options] [config] [start|stop|restart|reload|status]
#
# sr_sarra consumes message, for each message it downloads the product
# and reannounce it. On usage of sarra is to acquire data from source
# that announce their products.  The other usage is to dessiminate products
# from other brokers/pumps.
#
# condition 1: from a source
# broker                  = where sarra is running (manager)
# exchange                = xs_source_user
# message                 = message.headers['to_clusters'] verified...
#                           is this message for this cluster
# product                 = downloaded under directory (option document_root)
#                         = subdirectory from mirror option  OR
#                           message.headers['rename'] ...
#                           can be trimmed by option  strip
# post_broker             = where sarra is running (manager)
# post_exchange           = xpublic
# post_message            = same as incoming message
#                           message.headers['source']  is set from source_user
#                           message.headers['cluster'] is set from option cluster from default.conf
#                           message is built from url option give
# log_exchange            = xlog
#
#
# condition 2: from another broker/pump
# broker                  = the remote broker...
# exchange                = xpublic
# message                 = message.headers['to_clusters'] verified...
#                           is this message for this cluster
# product                 = usually the product placement is mirrored 
#                           option document_root needs to be set
# post_broker             = where sarra is running (manager)
# post_exchange           = xpublic
# post_message            = same as incoming message
#                           message.headers['source']  left as is
#                           message.headers['cluster'] left as is 
#                           option url : gives new url announcement for this product
# log_exchange            = xs_"remoteBrokerUser"
#
#
#============================================================

#

import os,sys,time

try :    
         from sr_amqp           import *
         from sr_consumer       import *
         from sr_file           import *
         from sr_ftp            import *
         from sr_http           import *
         from sr_instances      import *
         from sr_message        import *
except : 
         from sarra.sr_amqp      import *
         from sarra.sr_consumer  import *
         from sarra.sr_file      import *
         from sarra.sr_ftp       import *
         from sarra.sr_http      import *
         from sarra.sr_instances import *
         from sarra.sr_message   import *

class sr_sarra(sr_instances):

    def __init__(self,config=None,args=None):
        sr_instances.__init__(self,config,args)
        self.defaults()
        self.configure()

    def check(self):

        # bindings should be defined 

        if self.bindings == []  :
           key = self.topic_prefix + '.#'
           self.bindings.append( (self.exchange,key) )
           self.logger.debug("*** BINDINGS %s"% self.bindings)

        # make a single list for clusters that we accept message for

        self.accept_msg_for_clusters      = [ self.cluster ]
        self.accept_msg_for_clusters.extend ( self.cluster_aliases )
        self.accept_msg_for_clusters.extend ( self.gateway_for  )

        # umask change for directory creation and chmod

        try    : os.umask(0)
        except : pass

    def close(self):
        self.consumer.close()
        self.hc_pst.close()

    def connect(self):

        # =============
        # create message if needed
        # =============

        if not hasattr(self,'msg'):
           self.msg = sr_message(self.logger)

        # =============
        # consumer
        # =============

        self.consumer          = sr_consumer(self)
        self.msg.log_publisher = self.consumer.publish_back()
        self.msg.log_exchange  = self.log_exchange

        # =============
        # publisher
        # =============

        # publisher host

        self.hc_pst = HostConnect( logger = self.logger )
        self.hc_pst.set_url( self.post_broker )
        self.hc_pst.connect()

        # publisher

        self.publisher = Publisher(self.hc_pst)
        self.publisher.build()
        self.msg.publisher    = self.publisher
        self.msg.pub_exchange = self.post_exchange


    def configure(self):

        # overwrite defaults
        # the default settings in most cases :
        # sarra receives directly from sources  onto itself
        # or it consumes message from another pump
        # we cannot define a default broker exchange

        # default broker and exchange None

        self.broker   = None
        self.exchange = None
        # FIX ME  log_exchange set to NONE
        # instead of xlog and make it mandatory perhaps ?
        # since it can be xlog or xs_remotepumpUsername ?

        # in most cases, sarra downloads and repost for itself.
        # default post_broker and post_exchange are

        self.post_broker    = None
        self.post_exchange  = 'xpublic'
        if hasattr(self,'manager'):
           self.post_broker = self.manager

        # Should there be accept/reject option used unmatch are accepted

        self.accept_if_unmatch = True

        # most of the time we want to mirror product directory and share queue

        self.mirror            = True
        self.queue_share       = True

        # installation general configurations and settings

        self.general()

        # arguments from command line

        self.args(self.user_args)

        # config from file

        self.config(self.user_config)

        # verify all settings

        self.check()

        self.setlog()

    def __do_download__(self):

        self.logger.info("downloading/copying into %s " % self.msg.local_file)

        try :
                if   self.msg.url.scheme == 'http' :
                     return http_download(self)

                elif self.msg.url.scheme == 'ftp' :
                     return ftp_download(self)

                elif self.msg.url.scheme == 'sftp' :
                     try    : from sr_sftp       import sftp_download
                     except : from sarra.sr_sftp import sftp_download
                     return sftp_download(self)

                elif self.msg.url.scheme == 'file' :
                     return file_process(self.msg)

                # user defined download scripts

                elif self.do_download :
                     return self.do_download(self)

        except :
                (stype, svalue, tb) = sys.exc_info()
                self.logger.error("Download  Type: %s, Value: %s,  ..." % (stype, svalue))
                self.msg.log_publish(503,"Unable to process")
                self.logger.error("Could not download")

        self.msg.log_publish(503,"Service unavailable %s" % self.msg.url.scheme)

    def help(self):
        print("Usage: %s [OPTIONS] configfile [start|stop|restart|reload|status]\n" % self.program_name )
        print("OPTIONS:")
        print("instances <nb_of_instances>      default 1")
        print("\nAMQP consumer broker settings:")
        print("\tbroker amqp{s}://<user>:<pw>@<brokerhost>[:port]/<vhost>")
        print("\t\t(MANDATORY)")
        print("\nAMQP Queue bindings:")
        print("\texchange             <name>          (MANDATORY)")
        print("\ttopic_prefix         <amqp pattern>  (default: v02.post)")
        print("\tsubtopic             <amqp pattern>  (default: #)")
        print("\t\t  <amqp pattern> = <directory>.<directory>.<directory>...")
        print("\t\t\t* single directory wildcard (matches one directory)")
        print("\t\t\t# wildcard (matches rest)")
        print("\tlog_exchange         <name>          (default: xlog)")
        print("\nAMQP Queue settings:")
        print("\tdurable              <boolean>       (default: False)")
        print("\texpire               <minutes>       (default: None)")
        print("\tmessage-ttl          <minutes>       (default: None)")
        print("\tqueue_name           <name>          (default: program set it for you)")
        print("\nFile settings:")
        print("\taccept    <regexp pattern>           (default: None)")
        print("\tdocument_root        <document_root> (MANDATORY)")
        print("\tinplace              <boolean>       (default False)")
        print("\toverwrite            <boolean>       (default False)")
        print("\tmirror               <boolean>       (default True)")
        print("\treject    <regexp pattern>           (default: None)")
        print("\tstrip      <strip count (directory)> (default 0)")
        print("\tdo_download          <script>        (default None)")
        print("\ton_file              <script>        (default None)")
        print("\nMessage settings:")
        print("\ton_message           <script>        (default None)")
        print("\trecompute_chksum     <boolean>       (default False)")
        print("\tsource_from_exchange <boolean>       (default False)")
        print("\turl                  <url>           (MANDATORY)")
        print("\nAMQP posting broker settings:")
        print("\tpost_broker amqp{s}://<user>:<pw>@<brokerhost>[:port]/<vhost>")
        print("\t\t(default: manager amqp broker in default.conf)")
        print("\tpost_exchange        <name>          (default xpublic)")
        print("\ton_post              <script>        (default None)")
        print("DEBUG:")
        print("-debug")

    # =============
    # __on_message__
    # =============

    def __on_message__(self):

        # no support for delete event

        if self.msg.sumflg == 'R' :
           self.logger.warning("delete message ignored")
           return False

        # the message has not specified a destination.
        if not 'to_clusters' in self.msg.headers :
           self.msg.log_publish(403,"Forbidden : message without destination amqp header['to_clusters']")
           self.logger.error("message without destination amqp header['to_clusters']")
           return False

        # this instances of sr_sarra runs,
        # for cluster               : self.cluster
        # alias for the cluster are : self.cluster_aliases
        # it is a gateway for       : self.gateway_for 
        # all these cluster names were put in list self.accept_msg_for_clusters
        # The message's target clusters  self.msg.to_clusters should be in
        # the self.accept_msg_for_clusters list

        # if this cluster is a valid destination than one of the "to_clusters" pump
        # will be present in self.accept_msg_for_clusters

        ok = False
        for target in self.msg.to_clusters :
           if  not target in self.accept_msg_for_clusters :  continue
           ok = True
           break

        if not ok :
           self.logger.warning("skipped : not for this cluster...")
           return False

        # invoke user defined on_message when provided

        if self.on_message : return self.on_message(self)

        return True

    def process_message(self):

        self.logger.info("Received %s '%s' %s" % (self.msg.topic,self.msg.notice,self.msg.hdrstr))

        #=================================
        # setting source and cluster if required
        #=================================

        if self.source_from_exchange :
           ok = self.set_source()
           if not ok : return False

        if not 'from_cluster' in self.msg.headers :
           ok = self.set_cluster()
           if not ok : return False

        #=================================
        # setting up message with sr_sarra config options
        # self.set_local     : how/where sr_subscribe is configured for that product
        # self.msg.set_local : how message settings (like parts) applies in this case
        #=================================

        self.set_local()
        self.msg.set_local(self.inplace,self.local_file,self.local_url)

        #=================================
        # now message is complete : invoke __on_message__
        #=================================

        ok = self.__on_message__()
        if not ok : return False

        #=================================
        # prepare download 
        # make sure local directory where the file will be downloaded exists
        #=================================

        # pass no warning it may already exists
        try    : os.makedirs(self.local_dir,0o775,True)
        except : pass

        #=================================
        # overwrite False, ask that if the announced file already exists,
        # verify checksum to avoid an unnecessary download
        #=================================

        need_download = True
        if not self.overwrite and self.msg.checksum_match() :
           self.msg.log_publish(304, 'not modified')
           self.logger.info("file not modified %s " % self.msg.local_file)

           # if we are processing an entire file... we are done
           if self.msg.partflg == '1' :  return False

           need_download = False

        #=================================
        # proceed to download  3 attempts
        #=================================

        if need_download :
           i  = 0
           while i < 3 : 
                 ok = self.__do_download__()
                 if ok : break
                 i = i + 1
           # could not download
           if not ok : return False

           # force recompute checksum

           if self.recompute_chksum :
              self.msg.compute_local_checksum()
              # When downloaded, it changed from the message... 
              # this is weird... means the file changed in the mean time
              # and probably reposted...
              # now posting of this file will have accurate checksum
              if not self.msg.local_checksum == self.msg.checksum :
                 self.msg.set_sum(self.msg.sumflg,self.msg.local_checksum)
                 self.msg.log_publish(205,'Reset Content : checksum')

           # if the part should have been inplace... but could not

           if self.inplace and self.msg.in_partfile :
              self.msg.log_publish(307,'Temporary Redirect')

           # got it : call on_part if a part

           if self.msg.partflg != '1' and self.on_part :
              ok = self.on_part(self)
              if not ok : return False

           # got it : call on_file if a file

           if self.msg.partflg == '1' and self.on_file :
              ok = self.on_file(self)
              if not ok : return False

        #=================================
        # publish our download
        #=================================

        if self.msg.partflg != '1' :
           if self.inplace : self.msg.change_partflg('i')
           else            : self.msg.change_partflg('p')

        self.msg.set_topic_url('v02.post',self.msg.local_url)
        self.msg.set_notice(self.msg.local_url,self.msg.time)
        self.msg.publish()
        self.msg.log_publish(201,'Published')

        if self.msg.partflg == '1' : return True
      
        # if dealt with a part... and inplace, try reassemble

        if self.inplace : file_reassemble(self)

        return True


    def run(self):

        # configure

        self.configure()

        # present basic config

        self.logger.info("sr_sarra run")

        # loop/process messages

        self.connect()

        while True :
              try  :
                      #  consume message
                      ok, self.msg = self.consumer.consume()
                      if not ok : continue

                      #  process message (ok or not... go to the next)
                      ok = self.process_message()

              except:
                      (type, value, tb) = sys.exc_info()
                      self.logger.error("Type: %s, Value: %s,  ..." % (type, value))

    def set_local(self):

        # relative path by default mirror 

        self.rel_path = '%s' % self.msg.path
        if 'rename' in self.msg.headers :
           self.rel_path = '%s' % self.msg.headers['rename']

        # if we dont mirror force  yyyymmdd/source in front

        if not self.mirror :
           yyyymmdd = time.strftime("%Y%m%d",time.gmtime())
           self.rel_path = '%s/%s/%s' % (yyyymmdd,self.msg.headers['source'],self.msg.path)

           if 'rename' in self.msg.headers :
              self.rel_path = '%s/%s/%s' % (yyyymmdd,self.msg.headers['source'],self.msg.headers['rename'])
              self.rel_path = self.rel_path.replace('//','/')

        token = self.rel_path.split('/')
        self.filename = token[-1]

        # if strip is used... strip N heading directories

        if self.strip > 0 :
           if self.strip > len(token) : token = [token[-1]]
           else :                       token = token[self.strip:]
           self.rel_path = '/'.join(token)


        self.local_dir  = ''
        if self.document_root != None :
           self.local_dir = self.document_root 
        if len(token) > 1 :
           self.local_dir = self.local_dir + '/' + '/'.join(token[:-1])

        # Local directory (directory created if needed)

        self.local_dir  = self.local_dir.replace('//','/')
        self.local_file = self.local_dir   + '/' + self.filename
        self.local_url  = urllib.parse.urlparse(self.url.geturl() + '/' + self.rel_path)

        # we dont propagate renaming... once used get rid of it
        if 'rename' in self.msg.headers : del self.msg.headers['rename']

    def set_cluster(self):
        if self.cluster == None :
           self.msg.log_publish(403,"Forbidden : message without cluster")
           self.logger.error("Forbidden : message without cluster")
           return False

        self.msg.set_from_cluster(self.cluster)
        return True

    def set_source(self):
        if self.msg.exchange[:3] != 'xs_' :
           self.logger.info("Forbidden? %s %s '%s' %s" % (self.msg.exchange,self.msg.topic,self.msg.notice,self.msg.hdrstr))
           self.msg.log_publish(403,"Forbidden : message without source")
           self.logger.error("Forbidden : message without source")
           return False

        source = self.msg.exchange[3:]
        self.msg.set_source(source)
        return True

    def reload(self):
        self.logger.info("%s reload" % self.program_name)
        self.close()
        self.run()

    def start(self):
        self.logger.info("%s start" % self.program_name)
        self.run()

    def stop(self):
        self.logger.info("%s stop" % self.program_name)
        self.close()
        os._exit(0)

# ===================================
# MAIN
# ===================================

def main():

    action = None
    args   = None
    config = None

    if len(sys.argv) >= 3 :
       action = sys.argv[-1]
       config = sys.argv[-2]
       if len(sys.argv) > 3: args = sys.argv[1:-2]

    sarra = sr_sarra(config,args)

    if   action == 'reload' : sarra.reload_parent()
    elif action == 'restart': sarra.restart_parent()
    elif action == 'start'  : sarra.start_parent()
    elif action == 'stop'   : sarra.stop_parent()
    elif action == 'status' : sarra.status_parent()
    else :
           sarra.logger.error("action unknown %s" % action)
           sys.exit(1)

    sys.exit(0)



# =========================================
# direct invocation
# =========================================

if __name__=="__main__":
   main()
