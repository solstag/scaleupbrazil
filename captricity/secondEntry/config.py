"""
manage configuration settings for our double-entry / captricity app
"""

import sys
import os
import json
import logging
import shutil

def move_file(src, dest):
  """
  move a file from src to dest; this is a wrapper for
  shutil.copy or shutil.move -- makes it easy to change from one
  to the other

  Args:
    src: the file to move
    dest: the destination (directory or full filename)
  Returns:
    whatever either shutil.copy() or shutil.move() does
  """

  # uncomment to copy (not move) files
  #return shutil.copy(src, dest)

  # uncomment to move (not copy) files
  # TODO
  # can't just use shutil.move because it complains if the
  # file is copied twice...
  res = shutil.copy(src, dest)
  os.remove(src)
  return res

def copy_file(src, dest):
  """
  copy a file from src to dest; this is a wrapper for
  shutil.copy
  (this wrapper is here so we can change the exact behavior
   during development / debugging, if we want)

  Args:
    src: the file to move
    dest: the destination (directory or full filename)
  Returns:
    whatever shutil.copy() does
  """

  # uncomment to copy (not move) files
  return shutil.copy(src, dest)

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
  except BaseException:
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
  except BaseException:
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
  except BaseException:
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

def read_already_staged(staged_file):
  """
  read in file that has a list of .pdf files that have already been staged
  """

  staged_files = []

  try:
    infile = open(staged_file)
  except IOError, msg:
    print "already staged logfile does not exist..."
    return []

  for line in infile:
    staged_files.append(line.strip())

  infile.close()

  return staged_files

def write_already_staged(staged_file, staged_files):
  """
  read in file that has a list of .pdf files that have already been staged
  """

  already_staged = read_already_staged(staged_file)

  already_staged = set(staged_files) | set(already_staged)

  try:
    outfile = open(staged_file, 'w')
  except IOError, msg:
    print "problem writing to already staged logfile..."
    raise

  for item in already_staged:
    outfile.write("%s\n" % item)      
  outfile.close()



