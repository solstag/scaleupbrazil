"""
classes and functions related to routing scanned brazil documents
through Captricity using survey paths 
"""

import sys
import os
import csv
import logging
import re
import pyPdf
import shutil
import datetime
import dateutil
from secondEntry import *
#from secondEntry import CensusBlockLookup, SurveyPathLookup, ScanClient

logger = logging.getLogger(__name__)

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
            if not self.id or not ScanFile.svplookup.is_valid_qid(self.id):
                msg = '{} does not appear to be a valid questionnaire id.'.format(self.id)
                complain("bad questionnaire id", msg, ValueError)

            # and keep track of the survey path this questionnaire should take
            self.survey_path = ScanFile.svplookup.lookup[self.id]
            if 'id' in self.survey_path.keys():
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
        take a ScanFile and chop the pdf up in order to send it through Captricity;
        copy each piece to the appropriate staging directory

        as an example, the pages of an individual questionnaire dealing with sibling histories
        will be sent through different templates / Captricity jobs based on how many siblings
        are reported about. split_pdf will extract the pages of the individual questionnaire
        that have sibling history data and copy them to the appropriate staging directory

        Args:
          dest_dir: the root directory that has the subdirectories that we should
                    stage to

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

    svptemplates = secondEntry.config.get_template_map()

    def __init__(self, configdir=os.path.expanduser("~/.scaleupbrazil")):

        self.configdir = configdir
        self.scandirs = secondEntry.config.get_scan_dirs(os.path.join(configdir, 'scan-directories.json'))
        self.unstarted_jobs = []
        self.started_jobs = []

    def questionnaires_in_dir(self, 
                              image_directory, 
                              pattern=ScanFile.scan_fn_pat,
                              move_bad=True):
      """
      given a directory and a file pattern, return a list of the questionnaires whose images
      are in the directory

      Args:
        image_directory: the directory to search for questionnaire files
        pattern: the regular expression to use to extract questionnaire files
                 (defaults to ScanFile.scan_fn_pat)

      Returns:
        a list of ScanFile objects, one for each file found in the directory
      """

      files = os.listdir(os.path.expanduser(image_directory))

      okfiles = filter(lambda x: re.match(pattern, os.path.splitext(x)[0], re.IGNORECASE), files)

      badfiles = set(files) - set(okfiles)

      if move_bad:
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
        except BaseException, obj:
            msg = 'error converting {} : {}'.format(f,obj)
            if move_bad:
                shutil.copy(os.path.join(os.path.expanduser(image_directory),f), 
                            self.scandirs['staging_error'])
                # TODO - eventually move instead of copy
            ScanFile.tracker.create_issue(title="error converting", message_text=msg)
            logger.error(msg)
        
        resfiles.append(thissf)

      return resfiles

    def stage_files(self, qs, stage_root_dir="~/Dropbox/brazil/scans-staging"):
        """
        route the scanned images in a given directory to appropriate staging
        directories and figure out which paths they should take through captricity

        Args:
            qs: a list of ScanFile objects, one per questionnaire to be split
            stage_root_dir: the root directory where the staged pdfs should be sent

        Returns:
            staged, not_staged
            where staged is a list of ScanFile objects that were successfully staged
            and not_staged is a lits of ScanFile objects that could not be staged.
        """

        staged = []
        not_staged = []

        for q in qs:
            try:
                q.split_pdf(os.path.expanduser(stage_root_dir))
                staged.append(q)
            except BaseException, msg:
                shutil.copy(q.fullpath, self.scandirs['staging_error'])
                not_staged.append(q)
                # TODO -- eventually move instead of copy
                msg = "ERROR splitting pdf {}: {}; moved to error directory".format(q.fullpath, msg.message)
                ScanFile.tracker.create_issue(title="error splitting pdf", message_text=msg)
                logger.error(msg)

        return staged, not_staged



    def create_jobs(self, stage_root_dir="~/Dropbox/brazil/scans-staging"):
        """
        create jobs and upload survey forms for all of the subdirectories
        of the given directory; each subdirectory should contain pdfs related
        to one template, as described by self.scandirs

        NB: for now, we're assuming that all of the survey paths described
        are for individual questionnaires. this could change if we start to handle
        other types of forms

        Args:
          stage_root_dir: the root directory where the subdirectories containing
                          scans to be uploaded to jobs are kept
        Returns:
          TODO -- think about this. a list of created jobs?
        """        

        try:
            client = ScanClient()
        except BaseException, msg:
            logger.error("Can't start ScanClient")
            raise

        logger.info('started creating jobs...')

        today = datetime.datetime.now()

        new_jobs = []

        # NB: for now, we're assuming that all of the survey paths described
        # are for individual questionnaires. this could change if we start to handle
        # other types of forms
        for section in Router.svptemplates.keys():
            for value in Router.svptemplates[section].keys():

                # get list of files in this directory
                thisdir = os.path.join(stage_root_dir, 
                                       'questionnaires',
                                       section + '_' + value)

                these_files = self.questionnaires_in_dir(thisdir, move_bad=False)

                # if the survey path entry is null here, there's nothing to do
                # so skip it...; also skip if there are no files to upload...
                # (eg if there are 0 outmigrants, we don't feed anything through
                #  the outmigrant path)
                if not Router.svptemplates[section][value] or len(these_files) == 0:
                    logger.info('skipping {}_{}'.format(section,value))
                    continue

                logger.info('starting {}_{}'.format(section, value))

                # create a job using the document appropriate for this survey path
                this_docid = Router.svptemplates[section][value]['document_id']

                this_job_name = '{} - {}_{}'.format(str(today.date()), section, value)

                this_job = client.new_job(document_id=this_docid,
                                          job_name=this_job_name)

                new_jobs.append(this_job)

                # go through and upload each file in the directory; associate
                # it with the job we just created
                # [ helpful for info on uploading instance sets:
                #   https://shreddr.captricity.com/developer/quickstart/completed-forms/ ]

                for this_scanfile in these_files:
                    logger.info('starting upload of {} to job {}'.format(this_scanfile.filename, this_job['id']))

                    this_file = this_scanfile.filename + this_scanfile.ext
                    this_fullpath = this_scanfile.fullpath
                    this_iset_name = '{} - {}'.format(this_job_name, this_file)

                    # TODO - consider making uploading files / creating isets
                    #        part of client class instead of router...
                    this_iset = client.create_instance_sets(this_job['id'],
                                                            {
                                                             'name' : this_iset_name,
                                                             'multipage_file' : open(this_fullpath) 
                                                            })


        logger.info('finished creating jobs')

        self.unstarted_jobs = self.unstarted_jobs + new_jobs

        return new_jobs

    def start_jobs(self):
        """
        start any jobs that have been created but not started
        (costs money!)        
        """

        try:
            client = ScanClient()
        except BaseException, msg:
            logger.error("Can't start ScanClient")
            raise

        if self.unstarted_jobs:
            logger.info('router is starting job submissions...')
            started, unstarted = client.start_questionnaire_jobs(self.unstarted_jobs)
            self.started_jobs.append(started)
            self.unstarted_jobs = []
            self.unstarted_jobs.append(unstarted)
        else:
            logger.info('router has no jobs to submit...')        






