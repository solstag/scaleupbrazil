#! /usr/bin/env python

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
from captricityTransfer import *

def main():
  api_token=get_token()
  client = Client(api_token)

  if 'info' in sys.argv:
    print 'Available methods:'
    list_available_methods = client.print_help
    print list_available_methods()
    print 'Document info:'
    print document_info(client)
    #print 'Documents to read:'
    #docs_to_read = client.read_documents()
    #print docs_to_read

  if 'test' in sys.argv:
    job_id = test_upload(client)
    # this step costs money!
    if 'money' in sys.argv:
      client.launch_job(job_id)
      print 'launched job...'

main()

