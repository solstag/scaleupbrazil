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

import sys, os, re, json
import captools.api
from captools.api import ThirdPartyApplication
from captools.api import Client
from captricityTransfer import *

def test_upload(client, date):

  today = datetime.datetime.now()

  indir = os.path.expanduser("~/.scaleupbrazil/scanned-forms/" + date)
  outdir = os.path.expanduser("~/.scaleupbrazil/scanned-forms/jpgs/" + date)  

  #rv = call(['./prepare-images.py', '-p', 'quest', '-i', indir, '-o', outdir])
  #print "returned {}".format(rv)
  rv = 0
  if rv != 0:
    # TODO - eventually make this more elegant...
    print "Error in image pre-processing"
    sys.exit()

  # figure out which questionnaires are in the directory
  questionnaire_ids = questionnaires_in_dir(outdir)

  # get the corresponding templates
  templates, template_page_dict = prep_questionnaire_jobs(questionnaire_id_list=questionnaire_ids)

  # create the jobs
  jobs = create_questionnaire_jobs(client, 
                                   templates, 
                                   template_page_dict, 
                                   outdir, 
                                   name_pattern="auto-job-{}-".format(str(today.date())))

  # start the jobs (costs $$$!)
  #start_questionnaire_jobs(client, jobs)

  # TODO -- print more of a summary
  print 'done...'



def old_test_upload(client):
  """ old test upload fn"""
  # document_id = 1969 is the full survey
  # document_id = 2319 is just a few fields
  job = new_job(client, document_id=1969, job_name='small-api-test')
  
  print "created job with id {}".format(job['id'])
  
  upload_questionnaires(client, job['id'],
                        ['28_00143', '28_00140'],
                        os.path.expanduser("~/.scaleupbrazil/scanned-forms"))

  print 'finished uploading questionnaires...'

  return job['id']


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
    test_upload(client, "20120731")



    #job_id = test_upload(client)
    # this step costs money!
    #if 'money' in sys.argv:
    #  client.launch_job(job_id)
    #  print 'launched job...'

main()

