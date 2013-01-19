"""
config.py

manage configuration settings for our double-entry / captricity app
"""

import sys
import os
import json

def get_scan_dirs(template_file="~/.scaleupbrazil/scan-directories.json"):
  """
  read in the file that has the directories related to scanning survey forms
  """

  try:
    infile = open(os.path.expanduser(template_file), 'r')
    res = json.load(infile)
    infile.close()
  except:
    print "ERROR opening scan directory configuration file ", template_file
    sys.exit()

  return res

def get_template_map(template_file):
  """
  read in the file that has the mapping from survey paths to the corresponding document/template IDs
  """

  ## TODO-EXCEPTION
  infile = open(os.path.expanduser(template_file), 'r')
  res = json.load(infile)
  infile.close()

  return res

def get_survey_paths(svypath_file):
  """
  read in the file that maps questionnaire IDs to the various templates that each questionnaire
  should use.
  """

  ## TODO-EXCEPTION
  infile = csv.DictReader(open(os.path.expanduser(svypath_file), 'r'))  
  ## the .csv file's first column is the row number, which we don't need
  svy_paths = [x for x in infile]  
  delblank = lambda x: x.pop('') and x
  svy_paths = map(delblank, svy_paths)

  return svy_paths

def get_diffs(diff_file):
  """
  read in the file which has information about the differences between the
  captricity and vargas results
  """

  ## TODO-EXCEPTION
  infile = csv.DictReader(open(os.path.expanduser(diff_file), 'r'))

  res = []

  for row in infile:
    res.append(row)

  return res


