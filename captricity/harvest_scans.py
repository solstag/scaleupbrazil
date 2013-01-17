#! /usr/bin/env python
# coding: utf-8

"""
   harvest_scans
   ~~~~~~~~~~~~~

   command-line utility which takes scans uploaded to the ftp server,
   and moves them from different scanners' accounts into one central
   directory
"""

import sys
import os
import shutil
import re
import argparse
import datetime
import logging
import logging.config
from captricityTransfer import *

def grab_filenames(topdir, regex = "\\.pdf$"):
  """
  grab all of files whose names match a given pattern below a given root directory

  Args:
    topdir: the directory to search from
    regex: the pattern that filenames must match (None if all files should be returned)

  Returns:
    a list whose entries contain the paths to all of the files beneath
    topdir whose names match the pattern in regex
  """
  res = []

  for dirpath, dirnames, filenames in os.walk(top = topdir):
    res.extend([os.path.join(dirpath, f) for f in filenames if re.search(regex, f)])

  return res

def is_survey_scan(filename, cblookup):
  """
  determine whether or not the given filename is well-formed for a survey scan

  for now, there will be two types of survey scans: individual questionnaires and
  fico de campos. the individual questionnaires will match the format

    [15-digit census block id]_quest[5-digit id].[pdf|tiff]
  
  while the fichas de campo will match
  
    [15-digit census block id].[pdf|tiff]
  
    -OR-
  
    [15-digit census block id]_id[2 digits].[pdf|tiff]

  Args:
    filename: the filename to check
    cblookup: the census block lookup table, to be sure the given census block
              should be in the sample (see load_censusblocks())

  Returns:
    True if filename is a valid name for a survey scan; False otherwise
  """

  fn, ext = os.path.splitext(os.path.basename(filename))

  if not re.search("[pdf|tiff]", ext, re.IGNORECASE):
    return False

  if not re.search("\d{15}[_quest|_id|_id\d{2}]?", fn, re.IGNORECASE):
    return False

  if not cblookup.is_valid_censusblock(fn[:15]):
    return False

  return True

def main():

  logging.config.fileConfig(os.path.expanduser("~/.scaleupbrazil/logger.conf"))
  logger = logging.getLogger("scan")
  logger.propagate = False

  logger.info('harvest_scans started')

  dirs = config.get_scan_dirs()
  cblookup = sample.CensusBlockLookup()

  indirs = dirs["scanner_directories"]
  outdir = dirs["collected_raw_pdfs"]
  errdir = dirs["scan_error"]

  allpdfs = []

  # get the path of all of the PDFs in the raw scan upload directories
  for thisdir in indirs:
    logger.info('grabbing files from %s' % thisdir)
    allpdfs.extend(grab_filenames(os.path.expanduser(thisdir), "\\.pdf$"))

  # copy each file into the collected raw pdfs directory
  print 'moving files into collected raw pdfs directory:', outdir
  errcount = 0
  for f in allpdfs:

    if is_survey_scan(f, cblookup):
      logger.info('COPY %s to %s' % (f, os.path.join(outdir, os.path.basename(f))))
      #shutil.copy(f, outdir)
      # we may eventually want to move the scans instead of copying them
      #shutil.move(f, outdir)      
    else:
      logger.error('NO COPY - %s is not a survey scan; moved to error directory' % f)
      #shutil.copy(f, errdir)
      # we may eventually want to move the scans instead of copying them
      #shutil.move(f, errdir)      
      errcount += 1

  if errcount > 0:
    print "there were", errcount, "files that appear to be errors; check the log for more information."

  logger.info('harvest_scans finished [errcount = %s]' % str(errcount))

main()



