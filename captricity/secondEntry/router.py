"""
router.py

classes and functions related to routing scanned brazil documents
through Captricity using survey paths 
"""

import sys
import os
import csv
import logging
import re
from secondEntry.sample import CensusBlockLookup, SurveyPathLookup

logger = logging.getLogger(__name__)
logger.propagate = False

def get_template_map(template_file):
  """
  read in the file that has the mapping from survey paths to the corresponding document/template IDs
  """

  try:
    infile = open(os.path.expanduser(template_file), 'r')
    res = json.load(infile)
    infile.close()
  except:
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

class ScanFile(object):
    """
    description of a file containing a scanned survey document

    Attributes:
      fullpath: the full path to the file
      dir: directory
      filename: filename
      ext: file extension (currently, pdf and tiff are valid)
      censusblock: 15-digit census block
      type: one of "fichadecampo", "contactsheet" or "questionnaire"
      id: the id of the contactsheet or questionnaire; if the file is
          a ficha de campo, then id is None
    """

    scan_fn_pat = "(\d{15})_?(quest\d{5}|id\d{2})?"

    cblookup = CensusBlockLookup()
    svplookup = SurveyPathLookup()

    def __init__(self, file):
        """
        be sure to call the constructor with the full path and not just the filename
        """

        # see http://docs.python.org/2/howto/logging-cookbook.html
        # and http://stackoverflow.com/questions/7294127/python-cross-module-logging
        self.dir = os.path.dirname(file)
        self.filename, self.ext = os.path.splitext(os.path.basename(file))
        self.fullpath = file

        # figure out what type of file this is
        if not re.search("[pdf|tiff]", self.ext, re.IGNORECASE):
            raise ValueError('{} does not appear to be a pdf or tiff'.format(file))

        pat = re.match(ScanFile.scan_fn_pat, self.filename, re.IGNORECASE)

        if pat is None:
            raise ValueError('{} does not appear to be a well-formed scan file'.format(file))

        self.censusblock = pat.groups()[0]

        thistype = pat.groups()[1]

        if thistype is None:
            self.type = "fichadecampo"
            self.id = None
        elif "id" in thistype:
            self.type = "contactsheet"
            self.id = re.match("id(\d{2})", thistype).groups()[0]
        elif "quest" in thistype:
            self.type = "questionnaire"
            self.id = str(self.censusblock[:2]) + '_' + re.match("quest(\d{5})", thistype).groups()[0]
            # be sure the questionnaire ID is valid (could be problem with the filename)
            if not ScanFile.svplookup.is_valid_qid(self.id):
                raise ValueError('{} does not appear to be a valid questionnaire id.'.format(self.id))

            # and keep track of the survey path this questionnaire should take
            self.survey_path = ScanFile.svplookup.lookup[self.id]
        else:
            raise ValueError('This filename does not seem to be of the required type ({})'.format(thistype))

        # figure out if this census block is valid
        if not ScanFile.cblookup.is_valid_censusblock(self.censusblock):
            raise ValueError('{} does not appear to be from a valid census block in filename {}'.format(self.censusblock, file))

        self.blocktype = ScanFile.cblookup.cbs[self.censusblock]

    def split_pdf(self, dest_dir):

        if self.type == "questionnaire":
            logger.info('splitting {}'.format(self.filename))
            # TODO
        else:
            logger.info('not splitting {}, since it is not a questionnaire.'.format(self.filename))

class Router(object):

    def __init__(self, configdir=os.path.expanduser("~/.scaleupbrazil")):

        self.configdir = configdir

        ## TODO - read configuration file...

    def stage(self, image_directory, qtypes=["individual"]):
        """
        route the scanned images in a given directory to appropriate staging
        directories and figure out which paths they should take through captricity

        Args:
          image_directory: the directory containing the scans
          qtypes: a list whose entries can contain any of "individual", "contactsheet", "fichadecampo"
                  (possibly more later)
        Returns:
            TODO
        """

        # go through each file in the amalgamated directory
        # ...create a ScanFile object for it and keep track of it based on type

        pass #TODO              

    def questionnaires_in_dir(self, image_directory, pattern=ScanFile.scan_fn_pat):
      """
      given a directory and a file pattern, return a list of the questionnaires whose images
      are in the directory
      """

      files = os.listdir(os.path.expanduser(image_directory))

      okfiles = filter(lambda x: re.match(pattern, x), files)

      resfiles = []

      for f in okfiles:
        try:
            thissf = ScanFile(f)
            resfiles.append(thissf)
        except BaseException, obj:
            print 'error converting ', f, ':', obj.message
            pass

      return resfiles

    def stage_files(self, qs):

        for q in qs:
            q.split_pdf('temp')







