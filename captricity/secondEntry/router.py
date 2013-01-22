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
import secondEntry.trackercomm
import shutil

logger = logging.getLogger(__name__)
logger.propagate = False

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

def complain(title, msg, exceptiontype):
    """
    submit a bug report and then raise an exception
    """

    ScanFile.tracker.create_issue(title=title, message_text=msg)
    raise exceptiontype(msg)


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
    tracker = secondEntry.trackercomm.Tracker()

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
            msg = '{} does not appear to be a pdf or tiff'.format(file)
            complain("bad filetype", msg, ValueError)

        pat = re.match(ScanFile.scan_fn_pat, self.filename, re.IGNORECASE)

        if pat is None:
            msg = '{} does not appear to be a well-formed scan file.'.format(self.filename)
            complain("bad filename", msg, ValueError)

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
                msg = '{} does not appear to be a valid questionnaire id.'.format(self.id)
                complain("bad questionnaire id", msg, ValueError)

            # and keep track of the survey path this questionnaire should take
            self.survey_path = ScanFile.svplookup.lookup[self.id]
            del self.survey_path['id']
        else:
            msg = 'This filename does not seem to be of the required type ({})'.format(thistype)
            complain("wrong filename format", msg, ValueError)

        # figure out if this census block is valid
        if not ScanFile.cblookup.is_valid_censusblock(self.censusblock):
            msg = '{} does not appear to be from a valid census block in filename {}'.format(self.censusblock, file)
            complain("invalid census block", msg, ValueError)

        self.blocktype = ScanFile.cblookup.cbs[self.censusblock]

    def split_pdf(self, dest_dir):
        """
        TODO
        """

        try:
            thispdf = pyPdf.PdfFileReader(file(self.fullpath, 'rb'))
        except BaseException, msg:
            msg = 'error opening pdf file {} with pyPdf'.format(self.fullpath)
            complain("problem opening pdf file", msg, BaseException)

        if self.type == "questionnaire":

            # NB: if this gives us lots of trouble, we can avoid using getNumPages()
            # by running pdfinfo; see
            # http://www.quora.com/Which-Python-library-will-let-me-check-how-many-pages-are-in-a-PDF-file
            # (we're not doing this for now)
            if thispdf.getNumPages() != 22:
                msg = 'questionnaire {} does not have 22 pages!'.format(self.fullpath)
                complain("wrong number of pages", msg, BaseException)

            logger.info('splitting {}'.format(self.filename))

            for name, value in self.survey_path.iteritems():

                outdir = os.path.join(os.path.expanduser(dest_dir), 'questionnaires', name + '_' + str(value))

                if value not in ["0", "00"]:
                    thesepages = ScanFile.svptemplates[name][value]['pages']
                    destpdf = os.path.join(outdir, self.filename + '.pdf')

                    extract_pdf_pages(thispdf, destpdf, thesepages)

        elif self.type == "fichadecampo":
            if thispdf.getNumPages() != 2:
                msg = 'ficha de campo {} does not have 2 pages!'.format(self.fullpath)
                complain("wrong number of pages", msg, BaseException)

            logger.info('copying {}'.format(self.filename))

            outdir = os.path.join(os.path.expanduser(dest_dir), 'fichadecampo')
            outfile = os.path.join(outdir, self.filename + '.pdf')
            shutil.copy(self.fullpath, outfile)

        elif self.type == "contactsheet":
            if thispdf.getNumPages() != 2:
                msg = 'contact sheet {} does not have 2 pages!'.format(self.fullpath)
                complain("wrong number of pages", msg, BaseException)

            logger.info('copying {}'.format(self.filename))

            outdir = os.path.join(os.path.expanduser(dest_dir), 'contactsheet')
            outfile = os.path.join(outdir, self.filename + '.pdf')
            shutil.copy(self.fullpath, outfile)
        else:
            msg = 'file {} is of unknown type!'.format(self.fullpath)
            complain("unknown file type", msg, BaseException)

class Router(object):

    def __init__(self, configdir=os.path.expanduser("~/.scaleupbrazil")):

        self.configdir = configdir
        self.scandirs = secondEntry.config.get_scan_dirs(os.path.join(configdir, 'scan-directories.json'))

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

    def questionnaires_in_dir(self, image_directory, 
                              pattern=ScanFile.scan_fn_pat):
      """
      given a directory and a file pattern, return a list of the questionnaires whose images
      are in the directory
      """

      files = os.listdir(os.path.expanduser(image_directory))

      okfiles = filter(lambda x: re.match(pattern, os.path.splitext(x)[0], re.IGNORECASE), files)

      badfiles = set(files) - set(okfiles)

      for bf in badfiles:
        shutil.copy(os.path.join(os.path.expanduser(image_directory),bf), self.scandirs['staging_error'])
        # TODO -- eventually move instead of copy
        msg = "{} is not a well-formed filename! Moving to staging error directory...".format(bf)
        ScanFile.tracker.create_issue(title='bad filename', message_text=msg)
        logger.error(msg)

      resfiles = []

      for f in okfiles:
        try:
            thissf = ScanFile(os.path.join(os.path.expanduser(image_directory),f))
            resfiles.append(thissf)
        except BaseException, obj:
            msg = 'error converting {} : {}'.format(f,obj.message)
            shutil.copy(os.path.join(os.path.expanduser(image_directory),f), self.scandirs['staging_error'])
            # TODO - eventually move instead of copy
            ScanFile.tracker.create_issue(title="error converting", message_text=msg)
            logger.error(msg)

      return resfiles

    def stage_files(self, qs):
        """
        TODO
        """

        staged = []
        not_staged = []

        for q in qs:
            try:
                q.split_pdf("~/Dropbox/brazil/scans-staging")
                staged.append(q)
            except BaseException, msg:
                shutil.copy(q.fullpath, self.scandirs['staging_error'])
                not_staged.append(q)
                # TODO -- eventually move instead of copy
                msg = "ERROR splitting pdf {}: {}; moved to error directory".format(q.fullpath, msg.message)
                ScanFile.tracker.create_issue(title="error splitting pdf", message_text=msg)
                logger.error(msg)

        return staged, not_staged







