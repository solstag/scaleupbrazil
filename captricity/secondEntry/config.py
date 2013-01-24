"""
manage configuration settings for our double-entry / captricity app
"""

import sys
import os
import json
import logging

def start_log(configdir="~/.scaleupbrazil/logger.conf", logger_name="scan"):
  """
  start the default logger for the package...
  (TODO - eventually, this might go to more than one logfile
          eg for uploads vs downloads)
  """

  logging.config.fileConfig(os.path.expanduser("~/.scaleupbrazil/logger.conf"))
  logger = logging.getLogger(logger_name)
  logger.propagate = False

  return logger

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

def get_roundup_info(config_file="~/.scaleupbrazil/roundup.conf"):
  """
  get username / password for roundup account that the script will
  use to submit bugs, etc...
  """
  try:
    infile = open(os.path.expanduser(config_file), 'r')
    res = json.load(infile)
    infile.close()
  except:
    print "ERROR opening roundup tracker configuration file ", config_file
    sys.exit()

  return res  

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

def get_template_map(template_file="~/.scaleupbrazil/template-ids.json"):
  """
  read in the file that has the mapping from survey paths to the corresponding document/template IDs
  """

  try:
    infile = open(os.path.expanduser(template_file), 'r')
    res = json.load(infile)
    infile.close()
  except:
    print "ERROR opening template map..."
    sys.exit()

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


