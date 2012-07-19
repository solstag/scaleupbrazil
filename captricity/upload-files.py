#!/bin/env python

#####################################################################
# upload-files.py
#
# this file will take as input
#   -> a directory that has a bunch of pdfs that need to be scanned.
#      the filenames of these pdfs will correspond to the state code
#      and questionnaire IDs of each one
#   -> a table that maps state code / questionnaire ID to the template
#      that should be used in processing the file
#
# see:
#   https://shreddr.captricity.com/developer/quickstart/
#
# also, the examples in the captools library are useful
#

import sys
import os
import re
import captools.api
from captools.api import ThirdPartyApplication
from captools.api import Client

def get_token():
  """
  NB: assumes that the script was run in the scaleupbrazil/captricity directory
  """
  token_file = open('~/.scaleupbrazil/captricity-token')
  api_token = token_file.readlines()[0].strip()
  token_file.close()
  return api_token

def new_job ():
  """
  the full survey document id is 1969
  figured this out by hand using:
  NB: we don't want to do this all the time!
  created a job with id 2302 for us to
  play around with...
  """
  jobs = client.read_jobs()
  job_names = [x['name'] for x in jobs]
  job_docids = [x['document']['id'] for x in jobs]

  post_data = { 'document_id' : 1969,
                'name' : 'api-test-job' }
  job = client.create_jobs(post_data)
  return job

def main():
  if 'info' in sys.argv:
    list_available_methods = client.print_help
    list_available_methods()

  if 'register' in sys.argv:
    api_token=get_token()
    client = Client(api_token)
    docs_to_read = client.read_documents()

main()

