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
import pyPdf
from secondEntry.sample import CensusBlockLookup, SurveyPathLookup
import secondEntry.config
import shutil

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

def extract_pdf_pages(inpdf, outfile, pages):
    """
    take pages from a pdf file and save them in another pdf file

    Args:
        inpdf: the pyPdf.PdfFileReader object
        outfile: the filename to save the extracted pages to
        pages: a list of page numbers to extract
    Returns:
        nothing

    TODO -- should we handle exceptions here?
    """
    outpdf = pyPdf.PdfFileWriter()
    # see https://gist.github.com/2189062
    for page in pages:
        outpdf.addPage(inpdf.getPage(page))
    
    outstream = open(os.path.expanduser(outfile), 'wb')
    outpdf.write(outstream)
    outstream.close()

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

    scan_fn_pat = "(\d{15})(_quest\d{5}|_id\d{2})?$"    

    cblookup = CensusBlockLookup()
    svplookup = SurveyPathLookup()
    svptemplates = secondEntry.config.get_template_map()

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
        if not re.search("(pdf|tiff)", self.ext, re.IGNORECASE):
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
            self.id = re.match("_id(\d{2})", thistype).groups()[0]
        elif "quest" in thistype:
            self.type = "questionnaire"
            self.id = str(self.censusblock[:2]) + '_' + re.match("_quest(\d{5})", thistype).groups()[0]
            # be sure the questionnaire ID is valid (could be problem with the filename)
            if not ScanFile.svplookup.is_valid_qid(self.id):
                raise ValueError('{} does not appear to be a valid questionnaire id.'.format(self.id))

            # and keep track of the survey path this questionnaire should take
            self.survey_path = ScanFile.svplookup.lookup[self.id]
            del self.survey_path['id']
        else:
            raise ValueError('This filename does not seem to be of the required type ({})'.format(thistype))

        # figure out if this census block is valid
        if not ScanFile.cblookup.is_valid_censusblock(self.censusblock):
            raise ValueError('{} does not appear to be from a valid census block in filename {}'.format(self.censusblock, file))

        self.blocktype = ScanFile.cblookup.cbs[self.censusblock]

    def split_pdf(self, dest_dir):

        thispdf = pyPdf.PdfFileReader(file(self.fullpath, 'rb'))

        if self.type == "questionnaire":

            if thispdf.getNumPages() != 22:
                raise BaseException('questionnaire {} does not have 22 pages!'.format(self.fullpath))

            logger.info('splitting {}'.format(self.filename))

            for name, value in self.survey_path.iteritems():

                outdir = os.path.join(os.path.expanduser(dest_dir), 'questionnaires', name + '_' + str(value))

                if value not in ["0", "00"]:
                    thesepages = ScanFile.svptemplates[name][value]['pages']
                    destpdf = os.path.join(outdir, self.filename + '.pdf')

                    extract_pdf_pages(thispdf, destpdf, thesepages)

        elif self.type == "fichadecampo":
            if thispdf.getNumPages() != 2:
                raise BaseException('ficha de campo {} does not have 2 pages!'.format(self.fullpath))

            logger.info('copying {}'.format(self.filename))

            outdir = os.path.join(os.path.expanduser(dest_dir), 'fichadecampo')
            outfile = os.path.join(outdir, self.filename + '.pdf')
            shutil.copy(self.fullpath, outfile)

        elif self.type == "contactsheet":
            if thispdf.getNumPages() != 2:
                raise BaseException('contact sheet {} does not have 2 pages!'.format(self.fullpath))                

            logger.info('copying {}'.format(self.filename))

            outdir = os.path.join(os.path.expanduser(dest_dir), 'contactsheet')
            outfile = os.path.join(outdir, self.filename + '.pdf')
            shutil.copy(self.fullpath, outfile)
        else:
            raise BaseException('file {} is of unknown type!'.format(self.fullpath))

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

      okfiles = filter(lambda x: re.match(pattern, os.path.splitext(x)[0], re.IGNORECASE), files)

      badfiles = set(files) - set(okfiles)

      for bf in badfiles:
        logger.error("{} is not a well-formed filename!".format(bf))        

      resfiles = []

      for f in okfiles:
        try:
            thissf = ScanFile(os.path.join(os.path.expanduser(image_directory),f))
            resfiles.append(thissf)
        except BaseException, obj:
            print 'error converting ', f, ':', obj.message
            pass

      return resfiles

    def stage_files(self, qs):

        for q in qs:
            try:
                q.split_pdf("~/Dropbox/brazil/scans-staging")
            except BaseException, msg:
                logger.error("ERROR splitting pdf {}: {}".format(q.fullpath, msg.message))







