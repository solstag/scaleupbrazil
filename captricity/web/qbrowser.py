#! /usr/bin/env python
# coding=utf-8

import os
from os import path
import web
from web import form, safewrite
import sys, pymongo

# TODO - for now, this seems to work for getting the
# captricityTransfer library into the search path
# (but there must be a better way?)
sys.path.append(os.getcwd() + "/../")

import captricityTransfer as ct

db = pymongo.Connection().captools

render = web.template.render('templates/')

urls = ('/', 'index',
        '/adju/(\d{2}_\d{5})', 'questionnaire_id',
        '/adju/(\d{7}\d*)', 'shred_test',
        '/adju/shred/(\d{7}\d*)', 'shred_image')
app = web.application(urls, globals())


## NB: we may eventually want this to poll the API to get updated
## maps, instead of using the cached versions
qid_job, iset_qid, iset_shred, qid_shred = ct.load_useful_maps()
available_qids = qid_shred.keys()

class index: 
    pass
#     uploadform = form.Form( 
#         form.Dropdown(name='Questionario', args=quests, value=defaultquest),
#         form.File(name='Arquivo'))
#     def GET(self): 
#         form = self.uploadform()
#         return render.uploadscans(form)

#     def POST(self): 
#         form = self.uploadform() 
#         myinput = web.input(Arquivo={})
#         if not form.validates(): 
#             return render.uploadscans(form)
#         else:
#             safewrite(path.expanduser('~/.scaleupbrazil/uploadforms/')+form['Questionario'].value+'.pdf',
#                       myinput['Arquivo'].value)
#             quests.remove(form['Questionario'].value)
# #            return "Grrreat success! Questionnaire {} uploaded.<br/>".format(form['Questionario'].value)
#             if quests:
#                 return render.uploadscans(self.uploadform())
#             else:
#                 return 'Congratulations, you are done!'

class questionnaire_id: 
    def GET(self, questionnaire_id): 

        # grab the shreds for this questionnaire
        shreds = qid_shred[questionnaire_id]

        return render.questionnaire_test(questionnaire_id, zip(shreds.keys(), shreds.values()))

class shred_test: 
    def GET(self, shred_id): 
        return render.shred_test(shred_id)

class shred_image: 
    def GET(self, shred_id): 

        web.header("Content-Type", "images/jpeg")
        res = db.testimage.find_one({'id' : shred_id})

        return res['image_data']


if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()
