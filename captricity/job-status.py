#!/usr/bin/env python
"""
job_status.py
~~~~~~~~~~~~~

helper utility which gets the status of all of the jobs...

see:
  https://shreddr.captricity.com/developer/quickstart/

also, the examples in the captools library are useful
"""

import sys
import os
import re
import argparse
from secondEntry.apicomm import *

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
    
  client = ScanClient()

  print 'Jobs:'

  jobs = client.get_jobs(since_date=args.since_date,
                         only_complete=args.only_complete,
                         only_incomplete=args.only_incomplete,
                         name_pattern=args.name_pattern)
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
          print '\tdocument id:', job['document_id']
      print '\tjob id:', job['id']

if "__name__" == "__main__":
  main()
