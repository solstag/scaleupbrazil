"""
classes and functions related to interacting with the Brazil study sample
"""

import sys
import os
import csv
import logging

logger = logging.getLogger('scan.' + __name__)


class SurveyPathLookup(object):
	"""
	lookup table for info about survey paths for each interview
	"""

	def __init__(self, filename="~/.scaleupbrazil/survey-paths-for-captricity.csv"):
		  """
		  load a .csv file that describes which paths each interview took through
		  the survey. this tells us which of the templates we should apply.

		  the questionnaire IDs have the format
		    [2-digit state number]_[5-digit questionnaire ID]

		  Args:
		    filename: the .csv file containing the survey paths, produced by
		              auto-template-for-captricity.r
		  """

		  self.lookup = {}

		  try:
		    infile = open(os.path.expanduser(filename), 'r')
		    incsv = csv.DictReader(infile)
		    for x in incsv:
		      self.lookup[x['id']] = x
		    infile.close()
		  except BaseException, msg:
		  	logger.error("problem reading survey path file {} : {}".format(filename,
		  		                                                           str(msg)))
		  	raise

	def is_valid_qid(self, qid):
		"""
		check whether or not a given questionnaire ID is in the dataset
		(uses the output of auto-template-for-captricity.r)
		"""

		if qid in self.lookup.keys():
			return True
		return False

class CensusBlockLookup(object):
	"""
	lookup table for info about census blocks in our sample
	"""

	def __init__(self, filename="~/.scaleupbrazil/master-censusblock-list.csv"):
		  """
		  load a .csv file that describes which census blocks are and are not in our
		  sample

		  Args:
		    filename: the .csv file containing the census block info, produced by
		              sample-block-list.r
		  Returns:
		    a dictionary whose keys are census block ids, and whose values are
		    statuses: 
		       0 - never in sample
		       1 - always in sample
		       2 - currently in sample, as replacement
		       3 - previously in sample, but then replaced
		  """

		  self.cbs = {}

		  try:
		    infile = open(os.path.expanduser(filename), 'r')
		    incsv = csv.DictReader(infile)
		    for x in incsv:
		      self.cbs[x['census_block']] = int(x['status'])
		    infile.close()
		  except BaseException, msg:
		  	logger.error("problem reading census block file {} : {}".format(filename,
		  		                                                           str(msg)))
		  	raise

	def is_valid_censusblock(self, cb):
		"""
		given a census block, be sure that it has ever been in our sample
		(otherwise, we can't have any data from it)
		this list of census blocks is generated by sample-block-list.r

		Args:
		cb: the census block to check

		Returns:
		True: if the census block has ever been in our sample; False otherwise
		"""

		if not cb in self.cbs.keys():
			return False

		if self.cbs[cb] in [1,2,3]:
			return True
		else:
			return False

