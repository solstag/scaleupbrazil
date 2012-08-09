#! /usr/bin/env python
# coding=utf-8

from os import path
import web
from web import form, safewrite
import pymongo

db = pymongo.Connection().captools

render = web.template.render('templates/')

urls = ('/', 'index',
        '/adju/\d{2}_\d{5}', 'questionnaire_id',
        '/adju/(\d{7}\d*)', 'shred_test',
        '/adju/shred/(\d{7}\d*)', 'shred_image')
app = web.application(urls, globals())

quests = ['110087','110088','110089']
defaultquest = '110087'

class index: 
    uploadform = form.Form( 
        form.Dropdown(name='Questionario', args=quests, value=defaultquest),
        form.File(name='Arquivo'))
    def GET(self): 
        form = self.uploadform()
        return render.uploadscans(form)

    def POST(self): 
        form = self.uploadform() 
        myinput = web.input(Arquivo={})
        if not form.validates(): 
            return render.uploadscans(form)
        else:
            safewrite(path.expanduser('~/.scaleupbrazil/uploadforms/')+form['Questionario'].value+'.pdf',
                      myinput['Arquivo'].value)
            quests.remove(form['Questionario'].value)
#            return "Grrreat success! Questionnaire {} uploaded.<br/>".format(form['Questionario'].value)
            if quests:
                return render.uploadscans(self.uploadform())
            else:
                return 'Congratulations, you are done!'

class questionnaire_id: 
    def GET(self): 
        return "Trying to adjudicate..."

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
