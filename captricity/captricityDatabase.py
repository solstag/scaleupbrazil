#!/usr/bin/env python
"""
functions used in transferring data to and from the database
"""

import sys, os, re, json, csv, requests
import captools.api
from captools.api import ThirdPartyApplication
from captools.api import Client
import time, datetime, dateutil.parser
from subprocess import call
import pymongo
from pymongo import Connection
from captricityTransfer import *


def connect_to_database():
	"""
	return a database connection object
	"""

	return Connection().captools

def insert_diffs(db, diff_data):
  """
  take a list of the form [ (questionnaire_id, variable_name), ..., (qid, vname)]
  whose entries are questionnaire items where captricity and vargas produced different
  values. insert this list into the database.
  """

  # upsert questionnaire id and variable number for everything; if we overwrite
  # old ones, that's fine -- these should never change

  for qid, vnum in diff_data:
  	print 'going to try to insert quest num ', qid, 'and variable', vnum

  	# TODO -- need to add other fields
  	#    
  	basic_entry = { "$set" : {"questionnaire_id" : qid,
  	         	              "var" : vnum} }

  	db.item_diffs.update({"questionnaire_id" : qid,
  		                  "var" : vnum },
  		      			 basic_entry,
  		      			 upsert = True)

  # now all of the questionnaire_id / var values are in the database,
  # but some will already have all of their info filled out, and some
  # (which are new) will not. the new ones will not having anything in
  # their status field, so we'll search based on that
  newdiffs = db.item_diffs.find({ "status" : {"$exists" : False }})

  # TODO -- eventually, we should figure out when to load the locally cached versions,
  # and when to re-ping the API
  qid_job, iset_qid, iset_shred, qid_shred = load_useful_maps()

  if newdiffs:

  	now = datetime.datetime.now()

  	# TODO -- here, for each new diff, we need to fill in
  	# date_added, last_updated, job_id, shred_image_id, and status
  	for newdiff in newdiffs:

  		this_shred_id = qid_shred[newdiff['questionnaire_id']][newdiff['var']]

  		db.item_diffs.update( { "questionnaire_id" : newdiff['questionnaire_id'],
  			                    "var" : newdiff['var'] },
  			                  { "$set" : {
  			                  		"date_added" : now,
  			                  		"last_updated" : now,
  			                  		"shred_image_id" : this_shred_id,
  			                  		"status" : "unexamined"
  			                  }} )


  return 

def print_all_diffs(db):

	for i in db.item_diffs.find():
		print i['questionnaire_id'], '/', i['var'], ':', i


if __name__ == "__main__":

	# test code
	db = connect_to_database()

	insert_diffs(db, [ ("28_00142", "Q202"), ("28_00142", "Q201"), ("28_00140", "Q201"), ("28_00144", "Q201")])
	insert_diffs(db, [ ("28_00142", "Q202"), ("28_00142", "Q504_mes")])	

	for item in db.item_diffs.find():
		print item



