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
  token_file = open(os.path.expanduser('~/.scaleupbrazil/captricity-token'))
  api_token = token_file.readlines()[0].strip()
  token_file.close()
  return api_token

def new_job (client, document_id = 1969, job_name="api-test-job"):
  """
  create a new job, which is a document (template) and
  one or many scanned-in surveys (image sets).
  the default document_id, 1969, is the entire individual questionnaire
  """

  post_data = { 'document_id' : document_id }
  job = client.create_jobs(post_data)
  put_data = { 'name' : job_name }
  job = client.update_job(job['id'], put_data)
  return job

def upload_questionnaires(client, job_id, questionnaire_ids, png_path):
  """
  Take a list of questionnaire IDs that should be uploaded, the id of the job that
  we  want to associate them with, and the path to the directory where they are
  stored.
  For each questionnaire to upload, read the png files for all of its pages in,
  associate it with an image set, and upload them.
  """

  for qid in questionnaire_ids:

    print "uploading questionnaire %s" % qid

    # grab the filenames for all of the pages associated with this questionnaire
    filenames = ["%s/quest_%s-%d.png" % (png_path, qid, x) for x in range(22)]

    # create an instance set to hold all of the page images for this questionnaire
    post_data = {'name' : qid}
    instance_set = client.create_instance_sets(job_id, post_data)

    # fill the instance set in with the images for each page of the questionnaire
    for page_number, filename in enumerate(filenames):
      post_data = {'image' : open(filename),
                   'image_name' : 'page %s' % page_number}
      client.create_iset_instance(instance_set['id'], page_number, post_data)
      print "... page %d" % page_number
    
  print "done."

def document_info(client):
  """Get information about all of the documents (templates) associated with
     client's account. This is useful for figuring out which document ID
     number is associated with a given job's document/template."""
  jobs = client.read_jobs()
  job_names = [x['name'] for x in jobs]
  job_ids = [x['id'] for x in jobs]  
  job_docids = [x['document']['id'] for x in jobs]

  return dict(zip(job_names, job_docids)), dict(zip(job_names, job_ids))

def main():
  if 'info' in sys.argv:
    list_available_methods = client.print_help
    list_available_methods()

  if 'register' in sys.argv:
    api_token=get_token()
    client = Client(api_token)
    docs_to_read = client.read_documents()

def test_upload():
  api_token=get_token()
  client = Client(api_token)
  # document_id = 1969 is the full survey
  # document_id = 2319 is just a few fields
  job = new_job(client, document_id=1969, job_name='small-api-test')

  print "created job with id %d" % job['id']
  
  upload_questionnaires(client, job['id'],
                        ['28_00143', '28_00140'],
                        os.path.expanduser("~/.scaleupbrazil/pngs"))

  job = client.read_job(job['id'])

  print 'finished uploading questionnaires...'
  # this step costs money!
  client.launch_job(job['id'])

  print 'launched job...'

  return client, job

main()
