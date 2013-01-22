"""
apicomm.py

classes and functions related to interacting with Captricity's api
these are built on top of Captricity's own captools library
"""

import sys
import os
import csv
import logging
import time
import datetime
import dateutil.parser
from subprocess import call
from captools.api import Client

def get_token(configdir):
  """
  get the captricity API token from a file in the specified directory

  Args:
    configdir: the directory with the configuration files; defaults to ~/.scaleupbrazil
  Returns:
    the api token stored in the file 'captricity-token'
  """
  # TODO-EXCEPTION
  token_file = open(os.path.join(os.path.expanduser(configdir), 'captricity-token'))
  api_token = token_file.readlines()[0].strip()
  token_file.close()
  return api_token

class ScanClient(Client):

  def __init__(self, configdir=os.path.expanduser("~/.scaleupbrazil/")):
    self.token = get_token(configdir)
    Client.__init__(self, self.token)


  def new_job (self, document_id = 1969, job_name="api-test-job"):
    """
    create a new job, which is a document (template) and
    one or many scanned-in surveys (image sets).
    the default document_id, 1969, is the entire individual questionnaire
    """
    # TODO-EXCEPTION - check document exists
    post_data = { 'document_id' : document_id }
    job = self.create_jobs(post_data)

    put_data = { 'name' : job_name }
    job = self.update_job(job['id'], put_data)
    return job

  def get_jobs(self, since_date = None, name_pattern = None,
               only_complete=False, only_incomplete=False):
    """
    get all of the jobs associated with an account; if necessary,
    select only the jobs that have finished since since_date,
    whose names match name_pattern, and/or which are complete.
    """
    jobs = self.read_jobs()

    if name_pattern != None:
      jobs = filter( lambda x: bool(re.search(name_pattern, x['name'])), jobs )

    if since_date != None:
      refdate = None

      if not isinstance(since_date, datetime.datetime):
        refdate = dateutil.parser.parse(since_date)
      else:
        refdate = since_date
        
      # NB: this relies on short-circuit evaluation of the and...
      jobs = filter( lambda x: ((x['finished'] != None) and
                                (dateutil.parser.parse(x['finished']) >  refdate)),
                     jobs)
    if only_complete == True:
      jobs = filter( lambda x: x['finished'] != None, jobs )

    if only_incomplete == True:
      jobs = filter( lambda x: x['finished'] == None, jobs )

    return jobs
    

  def document_info(self):
    """
    Get information about all of the documents (templates) associated with
    client's account. This is useful for figuring out which document ID
    number is associated with a given job's document/template.
    """

    jobs = self.read_jobs()
    job_names = [x['name'] for x in jobs]
    job_ids = [x['id'] for x in jobs]  
    job_docids = [x['document_id'] for x in jobs]

    return dict(zip(job_names, job_docids)), dict(zip(job_names, job_ids))  

  def upload_questionnaires(self, job_id, questionnaire_ids, 
                            image_path, pages=xrange(22)):
    """
    Take a list of questionnaire IDs that should be uploaded, the id of the job that
    we  want to associate them with, and the path to the directory where they are
    stored.
    For each questionnaire to upload, read the jpg files for all of its pages in,
    associate it with an image set, and upload them.

    NB: this function assumes that the questionnaire filenames have the form
         quest_QID-PGN.jpg
    where QID is the questionnaire ID (eg: 28_00143), and
          PGN is the page number (eg: 003)
    """

    # TODO-EXCEPTION
    # check that job_id exists and is unfinished

    # page numbers from prepare-images.py have three digits (w/ leading 0s)
    pages = ["{num:03d}".format(num=int(z)) for z in pages]

    for qid in questionnaire_ids:

      print "uploading questionnaire {}, pages {}".format(qid, pages)
      print "target job id: {}".format(job_id)

      # grab the filenames for all of the pages associated with this questionnaire
      filenames = ["{}/quest_{}-{}.jpg".format(image_path, qid, x) for x in pages]

      # TODO-EXCEPTION
      # check that the filenames exist/make sense, etc

      # create an instance set to hold all of the page images for this questionnaire
      post_data = {'name' : qid}
      instance_set = self.create_instance_sets(job_id, post_data)

      # this is a bit tricky: the page number of the instance set is not, in general,
      # the same as the page number of the questionnaire (which is what the filename is based on)
      # fill the instance set in with the images for each page of the questionnaire
      for page_number, filename in enumerate(filenames):
        post_data = {'image' : open(filename),
                     'image_name' : 'page {}'.format(pages[page_number])}

        # TODO-EXCEPTION - check for problems with POST
        self.create_iset_instance(instance_set['id'], page_number, post_data)
        print "... page {} ({} of questionnaire)".format(page_number, pages[page_number])
      
    print "done."




