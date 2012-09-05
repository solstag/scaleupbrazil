#! /usr/bin/env python
# coding=utf-8

from os import path
import web
from web import form, safewrite
import sys, os, datetime, json

# see http://code.google.com/p/modwsgi/wiki/ApplicationIssues
# for advice on how to handle mod_wsgi application working directories
thisdir = os.path.dirname(__file__)
sys.path.append(os.path.join(thisdir, ".."))

import captricityTransfer as ct
import captricityDatabase as cd

render = web.template.render(os.path.join(thisdir, 'templates/'))

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
# use mod_wsgi and apache for live server
# see http://webpy.org/install#apache
application = app.wsgifunc()

# got this tip from
# http://stackoverflow.com/questions/7382886/session-in-webpy-getting-username-in-all-classes
# without this, the session resets every time a new page is viewed (as far as i can tell)
if web.config.get('_session') is None:
    # also see
    # http://webpy.org/cookbook/mod_wsgi-apache
    # for help on sessions with mod_Wsgi / apache
    curdir = os.path.dirname(__file__)
    store = web.session.DiskStore(os.path.join(curdir, 'sessions'))
    session = web.session.Session(app, 
                                  store,
                                  initializer={'loggedin': False, 'privilege': 0})
    web.config._session = session
else:
    session = web.config._session

# read list of un-uploaded questionnaires
#      from db / file
quests = ct.get_vargas_questionnaires()

# TODO -- haven't deleted this yet since we might eventually
#         have the upload interface use letter or number codes
#         for the states
state_codes = [ 11, 12, 13, 14, 15, 16, 17,
                21, 22, 23, 24, 25, 26, 27, 28, 29,
                31, 32, 33, 35,
                41, 42, 43,
                50, 51, 52, 53]

# quick helper function to determine whether or not the user is logged in...
def logged_in():

    if 'loggedin' not in session:
        session.loggedin = False

    if session.loggedin == False:
        return False
    else:
        return True

class login:

    loginform = form.Form(form.Textbox(name="username"),
                          form.Password(name="password"),
                          form.Button(name="login"),
                          validators = [ form.Validator("Can't find user, or password is incorrect",
                                                         lambda f: cd.check_user(db, 
                                                                                 f['username'], 
                                                                                 f['password'])) ])



    def GET(self):
        if logged_in():
            return """
<h1>you are already logged in!</h1>. 
<a href="/uploadscans/logout">logout now</a> or <a href="/uploadscans/upload">go to upload tool</a>
"""

        # form w/ username and password
        form = self.loginform()
        return render.uploadscans_login(form)

    def POST(self):
        form = self.loginform()

        if not form.validates():
            web.debug("login form invalid...")
            return render.uploadscans_login(form)

        else:
            session.loggedin = True
            raise web.seeother('/uploadscans/upload')

class logout:

    def GET(self):
        session.loggedin = False
        raise web.seeother('/uploadscans/login')


class uploadtool: 

    # helper fn to determine whether or not the questionnaire number entered
    # is a valid one
    def check_qnum(form):
        if form['Questionario'] in quests:
            return True
        else:
            return False

    ## TODO -- add checks that fields aren't blank, match the expected patterns, etc
    ## also add check that file type is correct...
    ##  see http://webpy.org/form
    uploadform = form.Form( 
        form.Textbox(name='Questionario', id="qid"),
        form.File(name='Arquivo', default={}),
        form.Button(name='upload'),
        validators = [form.Validator("Questionario doesn't exist", check_qnum)])

    def GET(self):

        if not logged_in():
            raise web.seeother('/login')

        params = web.input(msg="")

        form = self.uploadform()
        return render.uploadscans(form, quests, len(quests), params['msg'])

    def POST(self): 

        if not logged_in():
            raise web.seeother('/uploadscans/login')

        params = web.input(msg="")

        form = self.uploadform() 

        if not form.validates(): 

            ## TODO -- there must be a better way to add arguments to
            ##         a redirect, but i haven't been able to find it yet
            web.debug('upload form failed validation...')
            return render.uploadscans(form, quests, len(quests), params['msg'])
            #raise web.seeother('/upload?msg=That appears to be an invalid questionnaire number.')

        else:

            qnum = form['Arquivo'].name

            # this is all to get the filename (on the client side),
            # which we need to determine that it's tiff or pdf...
            # see: https://groups.google.com/forum/?fromgroups=#!topic/webpy/2k3x6ULb5t8
            # and http://epydoc.sourceforge.net/stdlib/cgi.FieldStorage-class.html
            ri = web.webapi.rawinput()
            infilename = ri['Arquivo'].filename

            if infilename.lower().endswith('pdf'):
                filetype = 'pdf'
            elif infilename.lower().endswith('tiff'):
                filetype = 'tiff'
            else:
                raise web.seeother('/uploadscans/upload?msg=Unrecognized file type! I know pdf and tiff.')

            ## TODO -- determine whether questionnaire is pdf or tiff...
            fn = path.expanduser(save_dir) + '/' + form['Questionario'].value + '.' + filetype
            web.debug('writing to ' + fn)

            ## TODO -- detect problems here...
            safewrite(fn, form['Arquivo'].value)

            quests.remove(form['Questionario'].value)

            raise web.seeother('/uploadscans/upload?msg=Upload sucessful.')


if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()

