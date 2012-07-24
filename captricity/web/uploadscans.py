#! /usr/bin/env python
# coding=utf-8

from os import path
import web
from web import form, safewrite

render = web.template.render('templates/')

urls = ('/', 'index')
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

if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()

