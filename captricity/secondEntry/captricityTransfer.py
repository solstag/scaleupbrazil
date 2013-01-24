#!/usr/bin/env python

import sys, os, re, json, csv, requests, pickle
import captools.api
from captools.api import ThirdPartyApplication
from captools.api import Client
import time, datetime, dateutil.parser
from subprocess import call


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
  template_page_lookup = {}

  # go through each questionnaire and build up a dictionary which has
  # as keys the template/document id and as values the questionnaire ids
  # that should be used
  for idx, q in enumerate(svy_paths):
    for s in q.keys():
      if s == 'id':
        continue

      # TODO-EXCEPTION
      this_template = template_map[s][q[s]]
      if this_template != None:
        templates.setdefault(this_template['document_id'], []).append(q['id'])
        template_page_lookup[this_template['document_id']] = this_template['pages']

  return templates, template_page_lookup

def create_questionnaire_jobs(client, 
                              templates, 
                              template_page_lookup, 
                              image_path,
                              name_pattern=""):
  """
  given a dictionary whose keys are document/template ids and whose entries
  are questionnaire numbers, create jobs and upload the appropriate files.
  return the codes of the jobs
  """

  jobs = []

  for doc in templates.keys():

    ## TODO-EXCEPTION check that document/template exists
    newjob = new_job(client, doc, name_pattern+str(doc))

    jobs.append(newjob)

    ## TODO-EXCEPTION
    upload_questionnaires(client, 
                          newjob['id'], 
                          questionnaire_ids=templates[doc], 
                          pages=template_page_lookup[doc], 
                          image_path=image_path)

  return(jobs)


def get_qid_maps(client, job_ids = None):
  """
  given a list of job ids this function
  returns qid_job_map, iset_qid_map

  where

  qid_job_map - a dictionary which maps questionnaire ids to jobs
  iset_qid_map - a dictionary which maps instance set ids to questionnaire ids

  if no job ids are passed in, use all of the client's jobs  

  this assumes that the instance sets' names are the questionnaire ids
  eg, 12_34567
  """

  if job_ids is None:

    jobs = get_jobs(client)
    job_ids = [x['id'] for x in jobs]

  qid_job_map = {}
  iset_qid_map = {}

  for job_id in job_ids:

    isets = client.read_instance_sets(job_id)

    iset_ids = [x['id'] for x in isets]
    qids = [x['name'] for x in isets]

    for this_iset_id, this_qid in zip(iset_ids, qids):
      
      iset_qid_map[this_iset_id] = this_qid

      qid_job_map.setdefault(this_qid, [])
      qid_job_map[this_qid].append(job_id)

  return qid_job_map, iset_qid_map

def get_iset_maps(client, job_ids = None):
  """
  given a list of job ids, this function
  returns a dictionary from instance set ids to a dictionary whose entries have shred ids and variable names
  """

  if job_ids is None:
    jobs = get_jobs(client)
    job_ids = [x['id'] for x in jobs]

  iset_shred_map = {}

  # it takes forever to keep reading instances,
  # so we'll avoid grabbing them from the server more than once
  instance_stash = {}

  for this_job in job_ids:

    print 'getting instance sets for job ', this_job, '...',

    shreds = client.read_shreds(this_job)
    shred_ids = [x['id'] for x in shreds]
    shred_varnames = [x['field']['name'] for x in shreds]

    print 'read shreds...',

    instance_ids = [x['registered_instance']['instance_id'] for x in shreds]

    for iid in instance_ids:
      if not iid in instance_stash.keys():
        instance_stash[iid] = client.read_instance(iid)['instance_set_id']

    print 'done reading instances'

    iset_ids = [instance_stash[iid] for iid in instance_ids ]

    [iset_shred_map.setdefault(x,{}) for x in iset_ids]

    for this_iset_id, this_shred_id, this_shred_name in zip(iset_ids, shred_ids, shred_varnames):
      iset_shred_map[this_iset_id][this_shred_name] = this_shred_id

  return iset_shred_map

def get_qid_shred_map(iset_shred_map, iset_qid_map):
  """
  given maps from instance set ids to list of shreds and from
  instance set ids to questionnaire ids, return
  a map from questionnaire ids to a list of shreds
  """

  qid_shred_map = {}

  for this_iset_id, this_qid in iset_qid_map.iteritems():

    qid_shred_map.setdefault(this_qid, {})

    #import pdb; pdb.set_trace()

    # TODO -- add warning or error if iset_shred_map doens't have this image set
    qid_shred_map[this_qid].update(iset_shred_map[this_iset_id])

  return qid_shred_map

def create_useful_maps(client, name_pattern="apitest-job", cache_file="~/.scaleupbrazil/useful-maps"):
  """
  create a few data structures which are useful in relating Captricity resources to 
  substantive things we are interested in. cache these data structures in a file so
  that we don't have to continually ping the api. it takes a while to generate some
  of these data structures because we have to get some of them from the api rather indirectly

  this returns:
     qid_job - a map from questionnaire's id to the job ids that were run to process it
     iset_qid - maps instance set ids to the questionnaire they came from
     iset_shred - maps instance set ids to the list of shreds they produced
     qid_shred - maps questionnaires to all of the shreds that they produced
  """

  # TODO -- eventually, we might want to keep this info in the
  # database, instead of in memory / cached files

  relevant_jobs = get_jobs(client, name_pattern=name_pattern)
  job_ids = [j['id'] for j in relevant_jobs]

  print 'getting qid maps...'
  qid_job, iset_qid = get_qid_maps(client, job_ids)

  print 'getting iset maps...'
  iset_shred = get_iset_maps(client, job_ids)

  qid_shred = get_qid_shred_map(iset_shred, iset_qid)

  if cache_file:
    outfile = open(os.path.expanduser(cache_file), 'wb')
    pickle.dump(qid_job, outfile, pickle.HIGHEST_PROTOCOL)
    pickle.dump(iset_qid, outfile, pickle.HIGHEST_PROTOCOL)
    pickle.dump(iset_shred, outfile, pickle.HIGHEST_PROTOCOL)
    pickle.dump(qid_shred, outfile, pickle.HIGHEST_PROTOCOL)
    outfile.close()

  return qid_job, iset_qid, iset_shred, qid_shred

# qid_job, iset_qid, iset_shred, qid_shred = create_useful_maps(client)  

def load_useful_maps(cache_file="~/.scaleupbrazil/useful-maps"):
  """
  load locally cached versions of the useful maps that were created by
  create_useful_maps. see that fn for what maps are produced
  """

  infile = open(os.path.expanduser(cache_file), "rb")
  qid_job = pickle.load(infile)
  iset_qid = pickle.load(infile)
  iset_shred = pickle.load(infile)
  qid_shred = pickle.load(infile)
  infile.close()

  return qid_job, iset_qid, iset_shred, qid_shred

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
  
def load_var_maps(varfile="~/.scaleupbrazil/varname-map.json"):
  """
  load the JSON file which maps the variable names we use in our code
  to the internal variable names Captricity uses
  """

  ## TODO-EXCEPTION
  infile = open(os.path.expanduser(varfile), 'r')
  res = json.load(infile)
  infile.close()

  return res

def get_vargas_questionnaires(qfile="~/.scaleupbrazil/survey-paths.csv"):
  """
  load the ids of the surveys that are in the Vargas dataset
  """

  ## TODO-EXCEPTION
  infile = open(os.path.expanduser(qfile), 'r')
  incsv = csv.DictReader(infile)

  qids = [x['id'] for x in incsv]

  infile.close()

  return qids










def questionnaires_in_dir(image_directory, pattern="(quest_)([\d|_]+)"):
  """
  given a directory and a file pattern, return a list of the questionnaires whose images
  are in the directory
  """
  files = os.listdir(os.path.expanduser(image_directory))

  files = filter( lambda x: bool(re.search(pattern, x)), files )
  files = set([ re.search(pattern,x).group(2) for x in files ])

  return files

def upload_questionnaires(client, job_id, questionnaire_ids, 
                          image_path, pages=xrange(22)):
  """
  Take a list of questionnaire IDs that should be uploaded, the id of the job that
  we  want to associate them with, and the path to the directory where they are
  stored.
  For each questionnaire to upload, read the jpg files for all of its pages in,
  associate it with an image set, and upload them.

  NB: this function assumes that the questionnaire filenames have the form
       quest_QID-PGN.jpg
  where QID is the questionnaire ID (eg: 28_00143), and
        PGN is the page number (eg: 003)
  """

  # TODO-EXCEPTION
  # check that job_id exists and is unfinished

  # page numbers from prepare-images.py have three digits (w/ leading 0s)
  pages = ["{num:03d}".format(num=int(z)) for z in pages]

  for qid in questionnaire_ids:

    print "uploading questionnaire {}, pages {}".format(qid, pages)
    print "target job id: {}".format(job_id)

    # grab the filenames for all of the pages associated with this questionnaire
    filenames = ["{}/quest_{}-{}.jpg".format(image_path, qid, x) for x in pages]

    # TODO-EXCEPTION
    # check that the filenames exist/make sense, etc

    # create an instance set to hold all of the page images for this questionnaire
    post_data = {'name' : qid}
    instance_set = client.create_instance_sets(job_id, post_data)

    # this is a bit tricky: the page number of the instance set is not, in general,
    # the same as the page number of the questionnaire (which is what the filename is based on)
    # fill the instance set in with the images for each page of the questionnaire
    for page_number, filename in enumerate(filenames):
      post_data = {'image' : open(filename),
                   'image_name' : 'page {}'.format(pages[page_number])}

      # TODO-EXCEPTION - check for problems with POST
      client.create_iset_instance(instance_set['id'], page_number, post_data)
      print "... page {} ({} of questionnaire)".format(page_number, pages[page_number])
    
  print "done."

def download_job_data(client, job_ids):
  """
  download the data generated by a set of jobs

  returns a dict whose keys are job ids and whose entries
  are lists whose entries are datasets.
  (note that one job can apparently have more than one
   dataset associated with it)
  """

  datasets = dict.fromkeys(job_ids, [])

  for job_id in job_ids:

    # eventually, if we pass job objects instead of just ids into this fn,
    # we can print the readable name instead of the id...
    # print '\tdownloading: ', job['name']
    print '\tdownloading: ', job_id,

    datasets[job_id] = []

    for idx, ds in enumerate(client.read_datasets(job_id)):
      print 'ds is ', ds
      nextdata = client.read_dataset(ds['id'], accept="text/csv")
      datasets[job_id].append(nextdata)

    print '...done'

  return datasets


def job_data_to_csv(datasets, data_dir):
  """
  save downloaded datasets to a given directory in .csv format
  """

  print 'saving datasets to disk...'
  for jobid, data in datasets.iteritems():
    for idx, ds in enumerate(data):
        fn = os.path.join(os.path.expanduser(data_dir),
                          str(jobid) + "-" + str(idx) + ".csv")
        try:        
          datafile = open(fn, 'w')
          datafile.write(ds)
          datafile.close()
        except:
          print 'Error writing to file! Offending path: ', fn
          sys.exit()

def get_single_shred_image(client, shred_id):
  """
  return the data associated with a shred image based on the shred id
  """

  base_url = 'https://shreddr.captricity.com/api/shreddr/shred/{id}/image'
  req_url = base_url.format(id=shred_id)

  r = requests.get(req_url, headers={'X_API_TOKEN' : str(client.api_token),
                                     'X_API_VERSION' : '0.1'})

  return r.content

def get_job_shreds(client, job_id, out_dir, download_images=True):
  """
  retrieve shred objects (all except images) for a given job
  """

  shredlist = client.read_shreds(job_id)

  if download_images == False:
    return shredlist

  # this yields a list of shred objects as a dict
  # each shred object appears to have an entry called field, again a dict
  # each field has 

  # save the shred images
  shred_ids = [x['id'] for x in shredlist]  

  for this_shred_id in shred_ids:

    print 'reading shred ', this_shred_id,
    # NB: Client.read_shred_image is not working right now
    #     (df corresponded with support@captricity.com about this)
    #     as a workaround, wrote the get_single_shred_image fn
    #this_image = client.read_shred_image(this_shred_id)
    this_image = get_single_shred_image(client, this_shred_id)
    print '...done'

    fn = os.path.join(os.path.expanduser(out_dir),
                          str(job_id) + "-" + str(this_shred_id) + ".jpg")
    try:        
      datafile = open(fn, 'wb')
      datafile.write(this_image)
      datafile.close()
    except Exception, err:
      sys.stderr.write('ERROR: {}\n'.format(str(err)))
      sys.exit()    

  return shredlist

