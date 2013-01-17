#! /usr/bin/env python
# coding: utf-8

"""
   prep_scans
   ~~~~~~~~~~

   command-line utility which takes raw scans (the output of harvest_scans.py)
   and prepares them for uploading to Captricity

   NOT YET WRITTEN -- NEED TO CHANGE CODE BELOW
"""

import sys
import os
import re
import argparse
import datetime
import logging
import logging.config
from captricityTransfer import *

def main():

  logging.config.fileConfig(os.path.expanduser("~/.scaleupbrazil/logger.conf"))
  logger = logging.getLogger("scan")
  logger.propagate = False

  logger.info('prep_scans started')

  dirs = config.get_scan_dirs()

  # TODO -- think about this more: what if we need to run more than once in
  #         a given day?

  # TODO - process the pdfs/tiffs into jpgs...

  # TODO - remove the processed pdfs

  # for the questionnaires that we converted, figure out which paths they take through
  # the survey and get jobs ready to process them
  questionnaire_ids = questionnaires_in_dir(outdir)
  templates, template_page_dict = prep_questionnaire_jobs(questionnaire_id_list=questionnaire_ids)

  if not no_jobs:
	# create the jobs
  	#jobs = create_questionnaire_jobs(client, templates, template_page_dict, 
  	#                                 out_dir, 
  	#                                 name_pattern="auto-job-{}-".format(str(today.date()))

  if money_ok:
  	  pass
	  # start the jobs (costs $$$!)
  	  #start_questionnaire_jobs(client, jobs)


main()



