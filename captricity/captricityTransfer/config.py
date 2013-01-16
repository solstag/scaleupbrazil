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
