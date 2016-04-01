#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib
import logging
import json
import os
import datetime
import bcrypt
import cherrypy
from modules import templates


"""
   Initial implementation based on cherrypy-Auth example:
   http://tools.cherrypy.org/wiki/AuthenticationAndAccessRestrictions

   Everything User + Authentication related is implemented here.

   Main part is the AuthController, which offers the endpoints
    /auth/register      - Register a new User
    /auth/login         - Login with an existing user
    /auth/logout        - Logout a user
    /auth/getUserData   - Returns profile-data associated with user
    /auth/getStatistics - Returns statistics from current user aswell as the overall office

    Users are stored inside /config/users.db with passwords stored using salted bcrypt.
    The current Implementation will not scale very well, since it uses a simple json-database,
    but for a few dozen users the implementation overhead would be too high.
"""
dbFile = os.path.abspath('./config/users.db')

SESSION_KEY = '_cp_username'

Users = {}

Statistics = {
    'counters': {},
    'lastCoffees': []
}

coffeeCount = 10


def loadDB():
    """ Load user database """
    global Users, Statistics
    try:
        with open(dbFile, "r+") as jsonFile:
            fContent = json.loads(jsonFile.read())
            Users.update(fContent['Users'])
            Statistics.update(fContent['Statistics'])
    except IOError:
        logging.warning("No userdb Found. If we're running for the first time, this can be ignored.")
    except ValueError as e:
        logging.error(e)
        logging.error("Syntax Error in user-database %s.", dbFile)


def saveDB():
    global Users, Statistics
    newContent = {
        'Users': Users,
        'Statistics': Statistics
    }
    with open(dbFile, 'w') as jsonFile:
        json.dump(newContent, jsonFile, indent=4, sort_keys=True)


def addCount(name):
    ts = str(datetime.datetime.now())
    currUser = cherrypy.session.get(SESSION_KEY)
    Statistics['lastCoffees'].append({'timestamp': ts, 'name': name, 'user': currUser})
    if len(Statistics['lastCoffees']) > coffeeCount:
        Statistics['lastCoffees'] = Statistics['lastCoffees'][1::]
    if name not in Statistics['counters']:
        Statistics['counters'][name] = 1
    else:
        Statistics['counters'][name] += 1
    if currUser:
        if 'statistics' not in Users[currUser]:
            Users[currUser]['statistics'] = {
                'counters': {},
                'lastCoffees': []
            }
        Users[currUser]['statistics']['lastCoffees'].append({'timestamp': ts, 'name': name})
        if len(Users[currUser]['statistics']['lastCoffees']) > coffeeCount:
            Users[currUser]['statistics']['lastCoffees'] = Users[currUser]['statistics']['lastCoffees'][1::]
        if name not in Users[currUser]['statistics']['counters']:
            Users[currUser]['statistics']['counters'][name] = 1
        else:
            Users[currUser]['statistics']['counters'][name] += 1
    saveDB()


def check_credentials(username, password):
    """Verifies credentials for username and password.
    Returns None on success or a string describing the error on failure"""
    if username in Users and "pw" in Users[username]:
        if bcrypt.hashpw(password.encode('utf-8'), Users[username]["pw"].encode('utf-8')).decode('utf-8') == Users[username]["pw"]:
            return None
    return u"<p style='color: red'>Incorrect username or password.</p>"


def check_auth(*args, **kwargs):
    """A tool that looks in config for 'auth.require'. If found and it
    is not None, a login is required and the entry is evaluated as alist of
    conditions that the user must fulfill"""
    conditions = cherrypy.request.config.get('auth.require', None)
    # format GET params
    get_parmas = urllib.parse.quote(cherrypy.request.request_line.split()[1])
    if conditions is not None:
        username = cherrypy.session.get(SESSION_KEY)
        if username:
            cherrypy.request.login = username
            for condition in conditions:
                # A condition is just a callable that returns true orfalse
                if not condition():
                    # Send old page as from_page parameter
                    raise cherrypy.HTTPRedirect("/auth/login?from_page=%s" % get_parmas)
        else:
            # Send old page as from_page parameter
            raise cherrypy.HTTPRedirect("/auth/login?from_page=%s" % get_parmas)
    del kwargs
    del args

cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)


def require(*conditions):
    """A decorator that appends conditions to the auth.require config
    variable."""
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f
    return decorate


# Conditions are callables that return True
# if the user fulfills the conditions they define, False otherwise
#
# They can access the current username as cherrypy.request.login
#
# Define those at will however suits the application.

def member_of(groupname):
    def check():
        return cherrypy.request.login in Users and groupname in Users[cherrypy.request.login]["groups"]
    return check


def name_is(reqd_username):
    return lambda: reqd_username == cherrypy.request.login


def any_of(*conditions):
    """Returns True if any of the conditions match"""
    def check():
        for c in conditions:
            if c():
                return True
        return False
    return check


def all_of(*conditions):
    """Returns True if all of the conditions match"""
    def check():
        for c in conditions:
            if not c():
                return False
        return True
    return check


class AuthController(object):

    def __init__(self):
        loadDB()

    def on_login(self, username):
        """Called on successful login"""
        pass

    def on_logout(self, username):
        """Called on logout"""
        pass

    def get_loginform(self, username, msg="Enter login information", from_page="/"):
        """ Returns the login/register-page """
        return templates.get_template("auth.html").render(username=username, msg=msg, from_page=from_page)

    @cherrypy.expose
    def register(self, username_reg, password_reg, email, name):
        """ Registers a new User with the passed parameters """
        global Users
        if username_reg in Users:
            return 'User already exists.'
        if not username_reg or not password_reg or not email or not name:
            return 'Invalid paramters. Check your input.'
        Users[username_reg] = {
            'groups': [],
            'name': name,
            'email': email,
            'pw': bcrypt.hashpw(password_reg.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        }
        saveDB()
        return "1"

    @cherrypy.expose
    @require()
    @cherrypy.tools.json_out()
    def getUserData(self):
        if not cherrypy.session.get(SESSION_KEY):
            return {}
        if cherrypy.session.get(SESSION_KEY) not in Users:
            return {}
        data = Users[cherrypy.session.get(SESSION_KEY)].copy()
        data['username'] = cherrypy.session.get(SESSION_KEY)
        del data['pw']
        return data

    @cherrypy.expose
    @require()
    @cherrypy.tools.json_out()
    def getStatistics(self, filterNames="1"):
        uName = cherrypy.session.get(SESSION_KEY)
        if not uName:
            return {}
        if uName not in Users:
            return {}
        filterStats = Statistics.copy()
        if filterNames == "1":
            filterStats["lastCoffees"] = [{'timestamp': x['timestamp'], 'name': x['name']} for x in filterStats["lastCoffees"]]
        result = {
            'global': filterStats
        }
        if "statistics" in Users[uName]:
            result['user'] = Users[uName]['statistics']
        return result

    @cherrypy.expose
    def login(self, username=None, password=None, from_page="/"):
        """ If valid login-data is given, redirects user to from_page.
            Otherwise returns the login-page """
        if username is None or password is None:
            return self.get_loginform("", from_page=from_page)

        error_msg = check_credentials(username, password)
        if error_msg:
            return self.get_loginform(username, error_msg, from_page)
        else:
            cherrypy.session.regenerate()
            cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
            self.on_login(username)
            raise cherrypy.HTTPRedirect(from_page or "/")

    @cherrypy.expose
    def logout(self, from_page="/"):
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        sess[SESSION_KEY] = None
        if username:
            cherrypy.request.login = None
            self.on_logout(username)
        raise cherrypy.HTTPRedirect(from_page or "/")
