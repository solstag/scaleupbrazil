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
from secondEntry.sample import CensusBlockLookup

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

## TODO -- add logging...

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

    cblookup = CensusBlockLookup()

    def __init__(self, file):

        self.dir = os.path.dirname(file)
        self.filename, self.ext = os.path.splitext(os.path.basename(file))
        self.fullpath = file

        # figure out what type of file this is
        if not re.search("[pdf|tiff]", self.ext, re.IGNORECASE):
            raise ValueError('{} does not appear to be a pdf or tiff'.format(file))

        pat = re.match("(\d{15})_?([quest\d{5}|id\d{2}])?", self.filename, re.IGNORECASE)

        if pat is None:
            raise ValueError('{} does not appear to be a well-formed scan file'.format(file))

        self.censusblock = pat.groups()[0]

        thistype = pat.groups()[1]
        if thistype is None:
            self.type = "fichadecampo"
            self.id = None
        elif "id" in thistype:
            self.type = "contactsheet"
            self.id = re.match("id(\d{5})", thistype).groups()[0]
        elif "quest" in thistype:
            self.type = "questionnaire"
            self.id = re.match("quest(\d{5})")

        # figure out if this census block is valid
        if not ScanFile.cblookup.is_valid_censusblock(self.censusblock):
            raise ValueError('{} does not appear to be from a valid census block in filename {}'.format(self.censusblock, file))

        self.blocktype = ScanFile.cblookup.cbs[self.censusblock]

        # get the survey path we should take
        # TODO



class Router(object):

    def __init__(self, configdir=os.path.expanduser("~/.scaleupbrazil")):

        self.configdir = configdir

        ## TODO - read configuration file...

        self.survey_paths = get_survey_paths(os.path.join(self.configdir, 'survey-paths-for-captricity.csv'))
        self.template_map = get_template_map(os.path.join(self.configdir, 'template-ids.json'))

        ## TODO -- error if can't read configuration...

    def stage(image_directory, qtypes=["individual"]):
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

    def questionnaires_in_dir(image_directory, pattern="(quest_)([\d|_]+)"):
      """
      given a directory and a file pattern, return a list of the questionnaires whose images
      are in the directory
      """

      ## TODO -- write this so that we can eventually add hh roster, etc, without much extra effor
      ## TODO -- change all this to parse questionnaire type, etc...

      files = os.listdir(os.path.expanduser(image_directory))

      files = filter( lambda x: bool(re.search(pattern, x)), files )
      files = set([ re.search(pattern,x).group(2) for x in files ])

      return files

    def stage_files(questionnaire_ids):

        pass #TODO







