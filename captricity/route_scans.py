#!/usr/bin/env python
# coding: utf-8
"""
   route_scans
   ~~~~~~~~~~~~~

   command-line utility which takes scans collected by harvest_scans.py
   and splits them up into appropriate staging directories for uploading
   to captricity
"""
import logging, logging.config
import os, sys
from collections import defaultdict

logging.config.fileConfig(os.path.expanduser("~/.scaleupbrazil/logger.conf"))
logger = logging.getLogger("scan")
logger.propagate = False

import secondEntry.router as ser
import secondEntry.config as sec

def count_types(qs):
  """
  quick helper function to get the distribution of questionnaire types
  from a list of ScanFile objects
  """

  alltypes = [x.type for x in qs]

  tots = defaultdict(int)
  for a in alltypes:
    tots[a] += 1
  return tots

def print_counts(title, counts):
  """
  quick helper function to print and log questionnaire type counts
  """
  print title
  logger.info(title)
  for k,v in counts.iteritems():
    print '   ', k, ':', v
    logger.info('   {}:{}'.format(k,v)) 


def main():

  logger.info('route_scans started')	
  
  try:
    dirs = sec.get_scan_dirs()
    pdfpath = dirs['collected_raw_pdfs']
  except BaseException, msg:
    logger.error("ERROR trying to read configuration directories; exiting: {}.".format(msg.message))
    sys.exit()

  router = ser.Router()

  logger.info('starting router q search...')
  # get all all of the questionnaires in the raw scans directory
  res = router.questionnaires_in_dir(pdfpath)


  # split all of the questionnaires up and move them into the appropriate
  # staging directories
  staged, not_staged = router.stage_files(res)

  staged_counts = count_types(staged)
  not_staged_counts = count_types(not_staged)

  print_counts('staged:', staged_counts)
  print_counts('not-staged:', not_staged_counts)

  print 'finished routing...'
  logger.info('finished routing...')


  logger.info('route_scans ended')

if __name__=="__main__":
  main()
