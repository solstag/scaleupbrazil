#! /usr/bin/env python
# coding: utf-8
"""
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

#from secondEntry import *
from secondEntry.router import *

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

def main():

  logger.info('harvest_scans started')

  dirs = config.get_scan_dirs()
  
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
  okcount = 0
  for f in allpdfs:

    try:
      sf = ScanFile(f)
      logger.info('COPY {} to {}'.format(sf.filename, os.path.join(outdir, os.path.basename(f))))
      shutil.copy(f, outdir)
      # TODO we may eventually want to move the scans instead of copying them
      #shutil.move(f, outdir)
      okcount += 1 
    except ValueError, err:
      logger.error('NO COPY - {} is not a survey scan; moved to error directory; message: {}'.format(f, err.message))
      shutil.copy(f, errdir)
      # TODO we may eventually want to move the scans instead of copying them
      #shutil.move(f, errdir)      
      errcount += 1

  print "successfully harvested", okcount, "scans."
  if errcount > 0:
    print "there were", errcount, "files that appear to be errors; check the log for more information."

  logger.info('harvest_scans finished [errcount = {}; okcount = {}]'.format(errcount, okcount))

if __name__ == "__main__":
  main()



