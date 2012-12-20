#! /usr/bin/env python
#
# grab a day's worth of uploaded scans and 
import sys, os, re, argparse, datetime

#import captools.api
#from captools.api import ThirdPartyApplication, Client
from captricityTransfer import *

# TODO -- this should be able to be run in info mode, just to give
#         the status...

# TODO -- assert / figure out last time R script to get info from Vargas dataset
#         was run...

# TODO -- read these from a configuration file
rawdir = "TODO"
outdir = "TODO"

def main():
  parser = argparse.ArgumentParser(description='Grab and process the latest set of scans')
  
  parser.add_argument('-d', '--date', action="store",
                      dest="date", 
                      default=datetime.datetime.today().strftime("%Y%m%d"),
                      help="date to use for output directory (defaults to today; format: YYYYMMDD)")
  parser.add_argument('-m', '--money', action="store_true",
                      dest="money_ok", 
                      default=False,
                      help="OK to use money to start processing the images")
  parser.add_argument('-J', '--nojobs', action="store_true",
                      dest="no_jobs", 
                      default=False,
                      help="Don't create jobs, only process scans to jpgs")

  args = parser.parse_args()
 
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



