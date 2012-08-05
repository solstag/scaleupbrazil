#! /usr/bin/env python
# coding=utf-8

import web
from web import form, safewrite
from os import path
from random import randint

render = web.template.render('templates/')

urls = ('/', 'index')
app = web.application(urls, globals())

class challenger:
    def __init__(self):
        self.data = [dict(id='12432', captricity='110087', manual='110088', image='stitch_209.jpg'),
                     dict(id='4321',  captricity='13',     manual='12',     image='stitch_210.jpg')]
        self.key = str(randint(0,2**32))
    def current(self):
        return self.data[-1] if self.data else None
    def shift(self):
        self.key = str(randint(0,2**32))
        return self.data.pop()
    
challenges = challenger()

class index: 
    def consolidateform(self):
        return form.Form( 
            form.Textbox(name='consolidated'),
            form.Hidden(name='key', value=challenges.key),
            form.Checkbox(name='unreadable', checked=False))() 
    def GET(self): 
        if challenges.current():
            form = self.consolidateform()
            return render.consolidata(form, challenges.current()['image'])
        else:
            return 'Move along, nothing to see here!'

    def POST(self): 
        form = self.consolidateform() 
        if not form.validates(): 
            return render.consolidata(form, challenges.current()['image'])
        elif form['key'].value != challenges.key:
            return 'You are out of sync, please reload! ({},{})'.format(form['key'].value, challenges.key)
        else:
            savedir = path.expanduser('~/.scaleupbrazil/consolidated/')
            if form['unreadable'].checked:
                savedir = path.join(savedir, 'unreadable')
            safewrite( path.join(savedir, challenges.current()['id']), form['consolidated'].value)
            challenges.shift()
            if challenges.current():
                return render.consolidata(self.consolidateform(), challenges.current()['image'])
            else:
                return 'Congratulations, you are done!'

if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()

