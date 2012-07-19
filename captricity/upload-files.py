#####################################################################
# upload-files.py
#
# this file will take as input
#   -> a directory that has a bunch of pdfs that need to be scanned.
#      the filenames of these pdfs will correspond to the state code
#      and questionnaire IDs of each one
#   -> a table that maps state code / questionnaire ID to the template
#      that should be used in processing the file
#
# see:
#   https://shreddr.captricity.com/developer/quickstart/
#
# also, the examples in the captools library are useful
#
import sys
import os
import re
import captools.api
from captools.api import ThirdPartyApplication
from captools.api import Client

## read api token
## NB: assumes that the script was run in the scaleupbrazil/captricity directory
token_file = open('.captricity-token')
api_token = token_file.readlines()[0].strip()
token_file.close()

## NB: the application token should be stored in .captricity-token
client = Client(api_token)
## this lists all of the (dynamically-created) methods available to
## our client
client.print_help()

## create a new job
## the full survey document id is 1969
## figured this out by hand using:
##  jobs = client.read_jobs()
##  job_names = [x['name'] for x in jobs]
##  job_docids = [x['document']['id'] for x in jobs]

## NB: we don't want to do this all the time!
## created a job with id 2302 for us to
## play around with...
##post_data = { 'document_id' : 1969,
##              'name' : 'api-test-job' }
##job = client.create_jobs(post_data)













