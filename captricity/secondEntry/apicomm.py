"""
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
import secondEntry.config as sec
from captools.api import Client

logger = logging.getLogger('scan.' + __name__)

class ScanClient(Client):

  def __init__(self, configdir=os.path.expanduser("~/.scaleupbrazil/")):
    self.token = sec.get_token(configdir)
    Client.__init__(self, self.token)


  def new_job (self, document_id = 1969, job_name="api-test-job"):
    """
    create a new job, which is a document (template) and
    one or many scanned-in surveys (image sets).
    the default document_id, 1969, is the entire individual questionnaire

    Args:
      document_id: the id of the document (template) that the job will use
      job_name: the name to give this job. TODO FORMAT CONVENTION

    Returns:
      the job object that gets created
    Throws:
      TODO
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

    logger.info('getting jobs...')

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
    
  def start_questionnaire_jobs(self, jobs):
    """
    given a list of job id numbers, go through and start the jobs
    (this will cost money!)

    Args:
      jobs: a list of job objects to be submitted (not just the ids)
    Returns:
      ok_jobs, prob_jobs
      where ok_jobs is a list of jobs successfully submitted
      and prob_jobs is a list of jobs that could not be submitted
    """

    ok_jobs = []
    prob_jobs = []

    for job in jobs:
      ## TODO-EXCEPTION: double-check that the job exists
      ##   and is incomplete before launching...
      res = self.read_job_readiness(job['id'])

      if not res or not res['is_ready_to_submit']:
        prob_jobs.append(job)
        logger.error("Error: job {} not ready to submit".format(job['id']))
        continue

      price = self.read_job_price(job['id'])

      logger.info("submitting job {} at price {} cents".format(job['id'],
                                                               price['total_job_cost_in_cents']))

      # TEMP -- actual submission is disabled while fixing logging...
      #self.submit_job(job['id'], {})

      ok_jobs.append(job)

    return ok_jobs, prob_jobs

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





