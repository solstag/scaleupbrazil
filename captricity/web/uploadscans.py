#! /usr/bin/env python
# coding=utf-8

from os import path
import web
from web import form, safewrite
import sys, os, datetime, json

# TODO - for now, this seems to work for getting the
# captricityTransfer library into the search path
# (but there must be a better way?)
sys.path.append(os.getcwd() + "/../")

import captricityTransfer as ct
import captricityDatabase as cd

render = web.template.render('templates/')

today = datetime.datetime.now()
today_date = str(today.date())

save_dir = os.path.expanduser('~/.scaleupbrazil/scanned-forms/raw-scans/' + today_date)

# if the output directory doesn't exist, create it
if not (os.path.isdir(save_dir)):
    os.mkdir(save_dir)

urls = ('/', 'uploadtool',
        '/login', 'login',
        '/logout', 'logout',
        '/upload', 'uploadtool',
        '/toupload', 'toupload')

# can't use debug with sessions; see
# http://webpy.org/docs/0.3/sessions
#web.config.debug = False

app = web.application(urls, globals())

store = web.session.DiskStore('sessions')
session = web.session.Session(app, store,
                              initializer={'loggedin': 0, 'privilege': 0})

# read list of un-uploaded questionnaires
#      from db / file
quests = ct.get_vargas_questionnaires()
defaultquest = ''

loginform = form.Form(form.Textbox(name="username"),
                      form.Password(name="password"),
                      validators = [ form.Validator("Can't find user, or password is incorrect",
                                                    lambda i: True)])

state_codes = [ 11, 12, 13, 14, 15, 16, 17,
                21, 22, 23, 24, 25, 26, 27, 28, 29,
                31, 32, 33, 35,
                41, 42, 43,
                50, 51, 52, 53]

#### TODO -- LEFT OFF HERE;
####  figuring out user authentication
####  just found this
####     http://webpy.org/tutorial3
####  under 'User authentication' it looks like there's
####  a very useful example

def logged_in():
    if session.loggedin == False:
        return True
    else:
        return False

class login:

    def GET(self):
        if logged_in():
            return '<h1>you are already logged in!</h1>. <a href="/logout">logout now</a>'

        # form w/ username and password
        form = loginform()
        return render.uploadscans_login(form)

    def POST(self):
        form = loginform()

        if not form.validates():
            return 'no dice!'
        else:
            session.logged_in = True
            return 'ok!'
            #raise web.seeother('/uploadtool')

class logout:

    def GET(self):
        session.logged_in = False
        raise web.seeother('/login')


class uploadtool: 
    uploadform = form.Form( 
        form.Textbox(name='Questionario', id="qid"),
        form.File(name='Arquivo'))

    def GET(self):

        if not logged_in():
            return '<h1>you are not logged in!</h1>. <a href="/login">login now</a>'

        form = self.uploadform()
        return render.uploadscans(form, quests, len(quests))

    def POST(self): 
        if logged_in() != True:
            return '<h1>you are not logged in!</h1>. <a href="/login">login now</a>'

        return "not yet implemented..."

        form = self.uploadform() 
        myinput = web.input(Arquivo={})
        if not form.validates(): 
            return render.uploadscans(form)
        else:
            safewrite(path.expanduser(save_dir)+form['Questionario'].value+'.pdf',
                      myinput['Arquivo'].value)

            ## TODO -- LEFT OFF HERE:
            ##   * in input form, narrow down by state
            ##   * might make more sense to re-ping for list fo questionnaires
            ##     rather than just delete one from the old list
            quests.remove(form['Questionario'].value)
#            return "Grrreat success! Questionnaire {} uploaded.<br/>".format(form['Questionario'].value)
            if quests:
                return render.uploadscans(self.uploadform())
            else:
                return 'Congratulations, you are done!'

        return json.dumps(toret)

if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()

