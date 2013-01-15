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
from captricityTransfer import *

configfile = os.path.expanduser("~/.scaleupbrazil/rawscandirs")
outdir = os.path.expanduser("~/.scaleupbrazil/collectedrawpdfs")

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

  try:
    indirs = open(configfile).read().splitlines()
  except:
    print 'ERROR opening configuration file ', configfile
    sys.exit()

  allpdfs = []

  # get the path of all of the PDFs in the raw scan upload directories
  for thisdir in indirs:
    print 'grabbing files from ', thisdir
    allpdfs.extend(grab_filenames(os.path.expanduser(thisdir), "\\.pdf$"))

  # copy each file into the collected raw pdfs directory
  print 'moving files into collected raw pdfs directory:'
  print outdir
  for f in allpdfs:
    #print 'COPY ', f, ' to ', os.path.join(outdir, os.path.basename(f))
    shutil.copy(f, os.path.join(outdir, os.path.basename(f)))

main()



