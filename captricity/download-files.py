#!/bin/env python

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

def main():
  api_token=get_token()
  client = Client(api_token)

  jobs = client.read_jobs()


main()
