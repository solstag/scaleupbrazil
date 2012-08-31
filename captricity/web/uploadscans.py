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

# get today's date for use with directory structure...
today = datetime.datetime.now()
today_date = str(today.date())

save_dir = os.path.expanduser('~/.scaleupbrazil/scanned-forms/raw-scans/' + today_date)

# if the output directory doesn't exist, create it
if not (os.path.isdir(save_dir)):
    web.debug('creating output directory: ', save_dir)
    os.mkdir(save_dir)

db = cd.connect_to_database()

urls = ('/', 'uploadtool',
        '/login', 'login',
        '/logout', 'logout',
        '/upload', 'uploadtool',
        '/toupload', 'toupload')

app = web.application(urls, globals())

# got this tip from
# http://stackoverflow.com/questions/7382886/session-in-webpy-getting-username-in-all-classes
# without this, the session resets every time a new page is viewed
if web.config.get('_session') is None:
    store = web.session.DiskStore('sessions')
    session = web.session.Session(app, 
                                  store,
                                  initializer={'loggedin': False, 'privilege': 0})
    web.config._session = session
else:
    session = web.config._session

# read list of un-uploaded questionnaires
#      from db / file
quests = ct.get_vargas_questionnaires()
defaultquest = ''

loginform = form.Form(form.Textbox(name="username"),
                      form.Password(name="password"),
                      validators = [ form.Validator("Can't find user, or password is incorrect",
                                                    lambda f: cd.check_user(db, 
                                                                  f['username'], 
                                                                  f['password']))])

state_codes = [ 11, 12, 13, 14, 15, 16, 17,
                21, 22, 23, 24, 25, 26, 27, 28, 29,
                31, 32, 33, 35,
                41, 42, 43,
                50, 51, 52, 53]

# helper fn to determine whether or not the questionnaire number entered
# is a valid one
def check_qnum(form):
    if form['Questionario'] in quests:
        return True
    else:
        return False

# quick helper function to determine whether or not the user is logged in...
def logged_in():

    if 'loggedin' not in session:
        #web.debug("'loggedin' not in session; creating...")
        session.loggedin = False

    if session.loggedin == False:
        return False
    else:
        return True

class login:

    def GET(self):
        if logged_in():
            return '<h1>you are already logged in!</h1>. <a href="/logout">logout now</a> or <a href="/upload">go to upload tool</a>'

        params = web.input()

        ## TODO -- there must be a less verbose way to do this
        if 'msg' not in params.keys():
            thismsg = ""
        else:
            thismsg = params['msg']

        # form w/ username and password
        form = loginform()
        return render.uploadscans_login(form, thismsg)

    def POST(self):
        form = loginform()

        if not form.validates():
            raise web.seeother('/login?msg=Login failed.')
        else:
            session.loggedin = True
            raise web.seeother('/upload')

class logout:

    def GET(self):
        session.loggedin = False
        raise web.seeother('/login')


class uploadtool: 

    uploadform = form.Form( 
        form.Textbox(name='Questionario', id="qid"),
        form.File(name='Arquivo'),
        validators = [form.Validator("Questionario doesn't exist", check_qnum)])

    def GET(self):

        if not logged_in():
            raise web.seeother('/login')

        params = web.input()

        ## TODO -- there must be a less verbose way to do this
        if 'msg' not in params.keys():
            thismsg = ""
        else:
            thismsg = params['msg']

        form = self.uploadform()
        return render.uploadscans(form, quests, len(quests), thismsg)

    def POST(self): 

        if not logged_in():
            raise web.seeother('/login')

        params = web.input()

        ## TODO -- there must be a less verbose way to do this        
        if 'msg' not in params.keys():
            thismsg = ""
        else:
            thismsg = params['msg']
        form = self.uploadform() 

        if not form.validates(): 

            ## TODO -- there must be a better way to add arguments to
            ##         a redirect, but i haven't been able to find it yet
            raise web.seeother('/upload?msg=That appears to be an invalid questionnaire number.')
        else:

            qnum = form['Arquivo'].name

            ## TODO -- LEFT OFF HERE:
            ## want to be able to determine the file type from the
            ## upload form...
            web.debug("qnum value is " + qnum)
            import pdb; pdb.set_trace()

            if qnum.lower().endswith('pdf'):
                filetype = 'pdf'
            elif qnum.lower().endswith('tiff'):
                filetype = 'tiff'
            else:
                raise web.seeother('/upload?msg=Unrecognized file type! I know pdf and tiff.')

            ## TODO -- determine whether questionnaire is pdf or tiff...
            fn = path.expanduser(save_dir) + '/' + form['Questionario'].value + filetype
            web.debug('writing to ' + fn)

            safewrite(fn, form['Arquivo'].value)

            quests.remove(form['Questionario'].value)

            raise web.seeother('/upload?msg=Upload sucessful.')


if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()

