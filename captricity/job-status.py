#!/bin/env python

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
import captools.api
from captools.api import ThirdPartyApplication
from captools.api import Client
from captricityTransfer import *

def main():
  api_token=get_token()
  client = Client(api_token)

  print 'Jobs:'
  # see list-jobs-example.py in the captools examples
  jobs = client.read_jobs()
  for job in jobs:
      print job['name']
      print '\tstatus:', job['status']
      print '\tinstance set count:', job['instance_set_count']
      print '\tcreated:', job['created']
      print '\tstarted:', job['started']
      if job['finished'] == "None" and job['started'] != "None":
          print '\tpct complete:', job['percent_completed']
      elif job['finished'] != "None":
          print '\tfinished:', job['finished']            
          print '\tdocument:', job['document']['name'], '( id:', job['document']['id'], ')'
      print '\tjob id:', job['id']

main()
