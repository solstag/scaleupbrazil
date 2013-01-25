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
import secondEntry as se

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

  logger = se.config.start_log()

  logger.info('harvest_scans started')

  dirs = se.config.get_scan_dirs()
  
  indirs = dirs["scanner_directories"]
  outdir = dirs["collected_raw_pdfs"]
  errdir = dirs["harvesting_error"]

  allpdfs = []

  # get the path of all of the PDFs in the raw scan upload directories
  for thisdir in indirs:
    logger.info('grabbing files from %s' % thisdir)
    allpdfs.extend(grab_filenames(os.path.expanduser(thisdir), "\\.pdf$"))

  # get all of the pdfs already in the raw scans directory...
  already_scraped = os.listdir(outdir)

  already_errors = os.listdir(errdir)

  # copy each file into the collected raw pdfs directory
  logger.info('moving files into collected raw pdfs directory: {}'.format(outdir))
  errcount = 0
  okcount = 0
  notnewcount = 0
  alreadyerrcount = 0

  for f in allpdfs:

    try:
      this_file = os.path.basename(f)

      sf = se.ScanFile(f)
      logger.info('COPY {} to {}'.format(sf.filename, os.path.join(outdir, os.path.basename(f))))

      if not this_file in already_scraped:
        se.copy_file(f, outdir)
        okcount += 1
      else:
        notnewcount += 1

    except ValueError, err:
      # move this file to the error directory, unless it's already there...
      if not this_file in already_errors:        
        logger.error('NO COPY - {} is not a survey scan; moved to error directory; message: {}'.format(f, err.message))
        se.copy_file(f, errdir)
        msg = "Problem harvesting {}; it appears not to be a survey scan. Message: {}".format(f,str(err))
        title = "problem harvesting {}".format(f)
        se.ScanFile.tracker.create_issue(title=title, message_text=msg)
        errcount += 1
      else:
        logger.info('{} already in error directory; ignoring.'.format(f))
        alreadyerrcount += 1

  print "successfully harvested {} scans.".format(okcount)
  if notnewcount > 0:
    print "there were {} files that had already been harvested.".format(notnewcount)
  if alreadyerrcount > 0:
    print "there were {} files that had already been found to be errors.".format(alreadyerrcount)
  if errcount > 0:
    print "there were {} files that appear to be errors; check the log for more information.".format(errcount)


  logger.info('harvest_scans finished [errcount = {}; notnewcount = {}; alreadyerrcount = {}; okcount = {}]'.format(errcount, notnewcount, alreadyerrcount, okcount))

if __name__ == "__main__":
  main()



