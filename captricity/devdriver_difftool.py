#! /usr/bin/env python

# development driver for diff tool infrastructure

import sys, os, re, json
import captools.api
from captools.api import ThirdPartyApplication
from captools.api import Client
from captricityTransfer import *

def main():
	get_diffs("~/.scaleupbrazil/diffs.csv")

main()