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
from bson.binary import Binary
from pymongo import Connection
from captricityTransfer import *

def connect_to_database():
	"""
	return a database connection object
	"""

	return Connection().captools

def insert_shreds_from_jobs(client, db, job_ids):
	"""
	given a list of job_ids, get all of the shreds associated with those jobs and
	insert them in the database

	TODO-DB / NOTE: this might be faster if we change to use bulk inserts
	"""

	print 'slurping shreds...'

	for job_id in job_ids:
		print 'starting job', job_id

		# TODO -- eventually, make get_job_shreds() handle this...
		shreds = client.read_shreds(job_id)

		for shred in shreds:
			this_shred_id = shred['id']
			print this_shred_id, ',',
			this_image = get_single_shred_image(client, this_shred_id)

			db.shred_images.insert({ 'shred_id' : this_shred_id,
															 'image_data' : Binary(this_image) })
		print '\ndone!'


def insert_diffs(db, diff_data):
	"""
	take a list of dictionaries of the form 
	[ {'name' : '<questionnaire id>', 'variable' : '<variable name>', ... },
		...,
		{'name' : '<questionnaire id>', 'variable' : '<variable name>', ...} ]

	whose entries are questionnaire items where captricity and vargas produced different
	values. insert this list into the database, ensuring that we don't re-insert a diff
	that is already there
	"""

	# upsert questionnaire id and variable number for everything; if we overwrite
	# old ones, that's fine -- these should never change
	#import pdb; pdb.set_trace()

	for thisdiff in diff_data:

		qid = thisdiff['name']
		vnum = thisdiff['variable']
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
	vmap = load_var_maps()

	if newdiffs:

		now = datetime.datetime.now()

		# TODO -- here, for each new diff, we need to fill in
		# date_added, last_updated, job_id, shred_image_id, and status
		for newdiff in newdiffs:

			#import pdb; pdb.set_trace()
			new_qid = newdiff['questionnaire_id']
			new_var = newdiff['var']

			#import pdb; pdb.set_trace()
			## TODO -- LEFT OFF HERE:
			##   need to finish mapping Captricity names to
			##   our variable names
			##   we've got the groundwork; trick is now to incorporate changes
			##   that happen after line 83 of captricity-vargas-makediffs.r
			##   eg, when we collapse the hour/min vars to one
			##   (right now, failing on 'q109_month')
			##   ALSO / RELATED: need to handle case
			##   where there are multiple shreds to show per diff
			##   (eg hh:mm questions)

			this_shred_id = qid_shred[new_qid][vmap[new_var]]

			db.item_diffs.update( { "questionnaire_id" : new_qid,
														"var" : new_var },
													{ "$set" : {
															"date_added" : now,
															"last_updated" : now,
															"shred_image_id" : this_shred_id,
															"status" : "unexamined"
													}} )


	return 

def get_questionnaire_diffs(db, questionnaire_id):
	"""
	given a questionnaire id, return a list containing all of the
	diff entries in the database that relate to that questionnaire
	"""

	res = db.item_diffs.find( { "questionnaire_id" : questionnaire_id })

	these_diffs = []

	for i in res:
		these_diffs.append(i)

	return these_diffs

def print_all_diffs(db):

	for i in db.item_diffs.find():
		print i['questionnaire_id'], '/', i['var'], ':', i


if __name__ == "__main__":

	# test code
	db = connect_to_database()

	diffs = get_diffs("~/.scaleupbrazil/diffs.csv")
	insert_diffs(db, diffs)  

	# insert the diffs that are in the captricity-vargas-diffs.csv file, as long
	# as they do not already exist
	print 'diffs:'
	print '------'
	for item in db.item_diffs.find():
		print item

	print 'first 20 shreds'
	print '---------------'
	for item in db.shred_images.find(limit=20):
		print item.keys()




