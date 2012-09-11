#! /usr/bin/env python
# coding=utf-8

import os
from os import path
import web
from web import form, safewrite
import sys, pymongo

# TODO -- 
# next steps here:
#   * add user login / logout (and sessions, etc)
#   * add post method / backend code for registering diffs
#   * flesh out db schema / strategy in more detail
#   * think about syncronization and multiple use
#   * add nf design comments


# TODO - for now, this seems to work for getting the
# captricityTransfer library into the search path
# (but there must be a better way?)
sys.path.append(os.getcwd() + "/../")

import captricityTransfer as ct
import captricityDatabase as cd

db = pymongo.Connection().captools

render = web.template.render('templates/')

urls = ('/', 'index',
        '/adju/(\d{2}_\d{5})', 'questionnaire_id',
        '/adju/diffs/(\d{2}_\d{5})', 'questionnaire_diffs',        
        '/adju/(\d{7}\d*)', 'shred_test',
        '/adju/shred/(\d{7}\d*)', 'shred_image')
app = web.application(urls, globals())

# this is the form object for a single diff which
# the user will resolve
diff_form = form.Form(
            form.Textbox("ajdu_value", description="value"),
            form.Checkbox(name='blank', checked=False),
            form.Checkbox(name='unreadable', checked=False),
            form.Checkbox(name='very distorted', checked=False),
            form.Textbox("comment", description="comment")
            )


## NB: we may eventually want this to poll the API to get updated
## maps, instead of using the cached versions
qid_job, iset_qid, iset_shred, qid_shred = ct.load_useful_maps()
available_qids = qid_shred.keys()

class index: 

    def GET(self): 
        form = self.uploadform()
        return render.uploadscans(form)

class questionnaire_id: 
    def GET(self, questionnaire_id): 

        # grab the shreds for this questionnaire
        shreds = qid_shred[questionnaire_id]

        return render.questionnaire_test(questionnaire_id, 
                                         zip(shreds.keys(), 
                                             shreds.values()))

    def POST(self, questionnaire_id):

        pass

        ## TODO -- fill this in

class questionnaire_diffs: 
    def GET(self, questionnaire_id): 

        # grab the diffs for this questionnaire
        diffs = cd.get_questionnaire_diffs(db, questionnaire_id, limit=3)

        diff_shred_qs = [x['var'] for x in diffs]
        diff_shred_ids = [x['shred_image_id'] for x in diffs]

        df = diff_form()

        return render.questionnaire_diff_test(questionnaire_id,
                                              df,
                                              zip(diff_shred_qs,
                                                  diff_shred_ids))

    def POST(self, questionnaire_id):

        pass

        ## TODO -- need to write this part...

class shred_test: 
    def GET(self, shred_id): 
        return render.shred_test(shred_id)

class shred_image: 
    def GET(self, shred_id): 

        #web.header("Content-Type", "images/jpeg")
        web.header("Content-Type", "images/png")
        res = db.shred_images.find_one({'shred_id' : int(shred_id)})

        return res['image_data']


if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()
