import sys, os, re, json, csv
import captools.api
from captools.api import ThirdPartyApplication
from captools.api import Client
import time
import dateutil.parser
import datetime

def get_template_map(template_file):
  """
  read in the file that has the mapping from survey paths to the corresponding document/template IDs
  """

  infile = open(os.path.expanduser(template_file), 'r')
  res = json.load(infile)
  infile.close()

  return res

def get_survey_paths(svypath_file):
  """
  read in the file that maps questionnaire IDs to the various templates that each questionnaire
  should use.
  """

  infile = csv.DictReader(open(os.path.expanduser(svypath_file), 'r'))  
  ## the .csv file's first column is the row number, which we don't need
  svy_paths = [x for x in infile]  
  delblank = lambda x: x.pop('') and x
  svy_paths = map(delblank, svy_paths)

  return svy_paths

def prep_questionnaire_jobs(template_file="~/.scaleupbrazil/template-ids.json",
                            svypath_file="~/.scaleupbrazil/survey-paths.csv",
                            questionnaire_id_list=None):
  """
  read the list of questionnaire ids and skip patterns and decide which jobs should be started
  in order to process the data they contain (allowing for skip patterns)

  template_file - has the location of the file that describes the template/document ids
  svypath_files - has the location of the file that maps questionnaire ids to different skip patterns
  questionnaire_id_list - if specified, the list of questionnaires to look for (defaults to all of them)
  """

  template_map = get_template_map(template_file)
  svy_paths = get_survey_paths(svypath_file)

  if questionnaire_id_list != None:
    questionnaire_id_list = set(questionnaire_id_list)
    svy_paths = filter(lambda x: x['id'] in questionnaire_id_list, svy_paths)
    if len(svy_paths) == 0:
      raise BaseException('No entries matching requested survey ids in the survey paths file.')

  templates = {}

  # go through each questionnaire and build up a dictionary which has
  # as keys the template/document id and as values the questionnaire ids
  # that should be used
  for idx, q in enumerate(svy_paths):
    for s in q.keys():
      if s == 'id':
        continue

      this_template = template_map[s][q[s]]
      if this_template != None:
        templates.setdefault(this_template, []).append(q['id'])

  return templates



def get_jobs(client, since_date = None, name_pattern = None,
             only_complete=False, only_incomplete=False):
  """
  get all of the jobs associated with an account; if necessary,
  select only the jobs that have finished since since_date,
  whose names match name_pattern, and/or which are complete.
  """
  jobs = client.read_jobs()

  if name_pattern != None:
    jobs = filter( lambda x: bool(re.search(name_pattern, x['name'])), jobs )

  if since_date != None:
    # TODO - eventually, check to see if since_date is already a datetime; for now,
    # we'll assume it's a string
    refdate = None

    if not isinstance(since_date, datetime.datetime):
      refdate = dateutil.parser.parse(since_date)
    else:
      refdate = since_date
      
    # NB: this relies on short-circuit evaluation of the and...
    jobs = filter( lambda x: ((x['finished'] != None) and
                              (dateutil.parser.parse(x['finished']) >  refdate)),
                   jobs)
  if only_complete == True:
    jobs = filter( lambda x: x['finished'] != None, jobs )

  if only_incomplete == True:
    jobs = filter( lambda x: x['finished'] == None, jobs )

  return jobs
  

def document_info(client):
  """Get information about all of the documents (templates) associated with
     client's account. This is useful for figuring out which document ID
     number is associated with a given job's document/template."""
  jobs = client.read_jobs()
  job_names = [x['name'] for x in jobs]
  job_ids = [x['id'] for x in jobs]  
  job_docids = [x['document']['id'] for x in jobs]

  return dict(zip(job_names, job_docids)), dict(zip(job_names, job_ids))

def get_token():
  """
  get the captricity API token from a file in the ~/.scaleupbrazil directory
  """
  token_file = open(os.path.expanduser('~/.scaleupbrazil/captricity-token'))
  api_token = token_file.readlines()[0].strip()
  token_file.close()
  return api_token

def new_job (client, document_id = 1969, job_name="api-test-job"):
  """
  create a new job, which is a document (template) and
  one or many scanned-in surveys (image sets).
  the default document_id, 1969, is the entire individual questionnaire
  """

  post_data = { 'document_id' : document_id }
  job = client.create_jobs(post_data)
  put_data = { 'name' : job_name }
  job = client.update_job(job['id'], put_data)
  return job

def upload_questionnaires(client, job_id, questionnaire_ids, png_path):
  """
  Take a list of questionnaire IDs that should be uploaded, the id of the job that
  we  want to associate them with, and the path to the directory where they are
  stored.
  For each questionnaire to upload, read the png files for all of its pages in,
  associate it with an image set, and upload them.
  """

  for qid in questionnaire_ids:

    print "uploading questionnaire {}".format(qid)

    # grab the filenames for all of the pages associated with this questionnaire
    filenames = ["{}/quest_{}-{}.png".format(png_path, qid, x) for x in range(22)]

    # create an instance set to hold all of the page images for this questionnaire
    post_data = {'name' : qid}
    instance_set = client.create_instance_sets(job_id, post_data)

    # fill the instance set in with the images for each page of the questionnaire
    for page_number, filename in enumerate(filenames):
      post_data = {'image' : open(filename),
                   'image_name' : 'page {}'.format(page_number)}
      client.create_iset_instance(instance_set['id'], page_number, post_data)
      print "... page {}".format(page_number)
    
  print "done."

def test_upload(client):
  # document_id = 1969 is the full survey
  # document_id = 2319 is just a few fields
  job = new_job(client, document_id=1969, job_name='small-api-test')
  
  print "created job with id {}".format(job['id'])
  
  upload_questionnaires(client, job['id'],
                        ['28_00143', '28_00140'],
                        os.path.expanduser("~/.scaleupbrazil/scanned-forms"))

  job = client.read_job(job['id']) #? this really necessary?

  print 'finished uploading questionnaires...'

  return job['id']
