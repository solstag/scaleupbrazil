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
os.chdir('/Users/dennis/scaleupbrazil/captricity')
token_file = open('.captricity-token')
api_token = token_file.readlines()[0].strip()
token_file.close()

## NB: the application token should be stored in .captricity-token
client = Client(api_token)
client.print_help()

doc = client.read_documents()







