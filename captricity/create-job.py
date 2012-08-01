#! /usr/bin/env python

# create-job.py
#
# create a job with a document; this will be used as a utility in
# creating the different templates for each possible survey path

import sys
import os
import re
import argparse
import captools.api
from captools.api import ThirdPartyApplication
from captools.api import Client
from captricityTransfer import *

def main():

  parser = argparse.ArgumentParser(description='Create a captricity job with no imagesets but a template. Useful in creating the tempaltes for the different survey paths.')
  
  parser.add_argument('-n', '--name', action="store",
                      dest="job_name", default=None,
                      help="the name of the job to create")
  parser.add_argument('-d', '--documentid', action="store",
                      dest="document_id", default=None,
                      help="the id of the document/template to associate with the job")

  args = parser.parse_args()

  if args.job_name is None or args.document_id is None:
  	print "Error in arguments."
  	sys.exit()

  api_token=get_token()
  client = Client(api_token)

  newid = new_job(client, document_id=args.document_id,
  	              job_name=args.job_name)

  print "Created job with id", newid

main()



