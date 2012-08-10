#!/usr/bin/env python

#####################################################################
# download-files.py
#
# this file will take as input the id of a job; it will check
# to see if that job is finished and, if so, it will download
# the data
#
# TODO -- eventually, this should also grab the images associated with
#         each field and stuff them in a database
#
# see:
#   https://shreddr.captricity.com/developer/quickstart/
#
# also, the examples in the captools library are useful
#

import sys
import os
import re
import argparse
import captools.api
from captools.api import ThirdPartyApplication
from captools.api import Client
from captricityTransfer import *
from captricityDatabase import *
import datetime
import dateutil
import requests
from PIL import Image 
from StringIO import StringIO


def main():
  api_token=get_token()  
  client = Client(api_token)

  out_data_dir = os.path.expanduser("~/.scaleupbrazil/downloaded-data/")
  out_shred_dir = os.path.expanduser("~/.scaleupbrazil/downloaded-data/shred-test")  

  job_name_pattern = "apitest2-job"

  jobs = get_jobs(client, name_pattern=job_name_pattern)
  job_ids = [x['id'] for x in jobs]

  res = download_job_data(client, job_ids)
  job_data_to_csv(res, out_data_dir)
  print 'saved data to {}'.format(out_data_dir)

  #joblist = get_jobs(client, name_pattern="apitest-job")
  #shredlist = get_job_shreds(client, 2592, out_shred_dir, download_images=False)

  db = connect_to_database()
  insert_shreds_from_jobs(client, db, job_ids)

  #import pdb; pdb.set_trace()

def old_test():

  client = Client(api_token)

  # figure out the last time we downloaded data
  try:
    datefile = open(os.path.expanduser("~/.scaleupbrazil/lastdownload"))
    lastcheck = datefile.readline().strip()
    datefile.close()  
  except IOError:
    print "Error reading last download date -- using default."
    lastcheck = "20120101"
    
  lastcheck = dateutil.parser.parse(lastcheck)

  print 'last download was on ', str(lastcheck)

  ##jobs = get_jobs(client, since_date=lastcheck, only_complete=True)
  jobs = get_jobs(client, only_complete=True)  
  checktime = datetime.datetime.now()
  
  # download the data for each job
  datasets = []
  dataset_names = []

  for job in jobs:

    print '\tdownloading: ', job['name']

    for idx, ds in enumerate(client.read_datasets(job['id'])):
      nextdata = client.read_dataset(ds['id'], accept="text/csv")
      datasets.append(nextdata)
      dataset_names.append(str(job['id']) + '-' + str(idx))

  print 'saving datasets to disk...'
  for idx, ds in enumerate(datasets):
    try:
      fn = os.path.expanduser("~/.scaleupbrazil/downloaded-data/" +
                              dataset_names[idx] + ".csv")
      datafile = open(fn, 'w')
      datafile.write(datasets[idx])
      datafile.close()
    except:
      print 'Error writing to file! Offending path: ', fn
      sys.exit()
      
  # update the last check date
  print 'updating date of last download'
  datefile = open(os.path.expanduser("~/.scaleupbrazil/lastdownload"), "w")
  datefile.write(str(checktime))
  datefile.close()

  print 'done.'

main()
