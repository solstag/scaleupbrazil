#!/usr/bin/env python

#####################################################################
# job-status.py
#
# helper utility which gets the status of all of the jobs...
#
# TODO - eventually, should take a pattern in job names
#        to match against
#
# see:
#   https://shreddr.captricity.com/developer/quickstart/
#
# also, the examples in the captools library are useful
#

import sys
import os
import re
import argparse
#import captools.api
from captools.api import ThirdPartyApplication
from captools.api import Client
from captricityTransfer import *
from captricityTransfer.captricityTransfer import *

def main():
  parser = argparse.ArgumentParser(description='Check the status of Captricity jobs')
  
  parser.add_argument('-p', '--pattern', action="store",
                      dest="name_pattern", default=None,
                      help="only jobs whose name matches the given pattern")
  parser.add_argument('-d', '--date', action="store",
                      dest="since_date", default=None,
                      help="only jobs that finished since the given date (YYYYMMDD)")
  parser.add_argument('-c', '--completed', action="store_true",
                      dest="only_complete", default=False,
                      help="only jobs that have finished")
  parser.add_argument('-i', '--incomplete', action="store_true",
                      dest="only_incomplete", default=False,
                      help="only jobs that have not finished")  

  args = parser.parse_args()
    
  api_token=get_token()
  client = Client(api_token)

  print 'Jobs:'

  jobs = get_jobs(client,
                  since_date=args.since_date,
                  only_complete=args.only_complete,
                  only_incomplete=args.only_incomplete,
                  name_pattern=args.name_pattern)
  for job in jobs:
      #import pdb; pdb.set_trace()
      print job['name']
      print '\tstatus:', job['status']
      print '\tinstance set count:', job['instance_set_count']
      print '\tcreated:', job['created']
      print '\tstarted:', job['started']
      if job['finished'] == "None" and job['started'] != "None":
          print '\tpct complete:', job['percent_completed']
      elif job['finished'] != "None":
          print '\tfinished:', job['finished']            
          print '\tdocument id:', job['document_id']
      print '\tjob id:', job['id']

main()
