#! /usr/bin/env python
# coding=utf-8

from os import path
import web
from web import form, safewrite

render = web.template.render('templates/')

urls = ('/', 'index')
app = web.application(urls, globals())

class questionnaires:
    q = ['110087','110088','110089']
    def get(self):
        return self.q
    def default(self): 
        return '110087'
    def remove(self, value):
        self.q.remove(value)


class index: 
    uploadform = form.Form( 
        form.Dropdown(name='Questionario', args=questionnaires.get(), value=questionnaires.default() ),
        form.File(name='Arquivo'))
    def GET(self): 
        form = self.uploadform()
        return render.formtest(form)

    def POST(self): 
        form = self.uploadform() 
        myinput = web.input(Arquivo={})
        if not form.validates(): 
            return render.formtest(form)
        else:
            safewrite(path.expanduser('~/.scaleupbrazil/uploadforms/')+form['Questionario'].value+'.pdf',
                      myinput['Arquivo'].value)
            questionnaires.remove(form['Questionario'].value)
            return "Grrreat success! Questionnaire {} uploaded.<br/>".format(form['Questionario'].value)+render.formtest(form)

if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()

