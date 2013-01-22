"""
trackercomm.py

classes and functions related to interacting with the roundup
tracker that we're going to use to keep track of problems...
"""

import sys
import os
import secondEntry.config
from roundup import instance, date
import logging

logger = logging.getLogger(__name__)
logger.propagate = False

class Tracker(object):

  def __init__(self, config_file="~/.scaleupbrazil/roundup.json"):
    """
    object to handle interacting with issue tracker

    in the roundup install files, see scripts/add-issue
    for code that was helpful as a model here
    """

    try:
      self.config = secondEntry.config.get_roundup_info(config_file)
    except BaseException:
      #logger.error("can't open the configuration file for the tracker user.")
      sys.exit()


  def create_issue(self, title, message_text):
    """
    TODO 
      - write docs
      - eventually add summary, title
    """
    ## in the roundup install files, see scripts/add-issue
    ## for the code i used as a model
    try:
      tracker = instance.open(self.config['tracker'])
      db = tracker.open('admin')
      uid = db.user.lookup(self.config['user']['username'])
      db.close()
  
      db = tracker.open(self.config['user']['username'])
      #db = tracker.open('user')      

      thismsg = []

      if message_text:
        thismsg = [db.msg.create(content=message_text,
                                 author=uid, date=date.Date())]
      #res=db.bug.create(title=title, 
      #                  messages=thismsg)
      res=db.issue.create(title=title, 
                        messages=thismsg)      

      db.commit()

    except BaseException, msg:
      logger.error("Exception raised when trying to add issue to tracker in create_issue: {}".format(msg.message))
      #import pdb; pdb.set_trace()
      pass
    finally:
      if db:
        db.close()





