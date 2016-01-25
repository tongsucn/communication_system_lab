#!/usr/bin/python

import logging
import json
import os
import time
import datetime
from threading import Thread
import cherrypy
import modules
from modules import settings
from modules import auth
from modules import templates
from modules import cmachine

cherrypy.log.screen = False
"""
    Global cherrypy settings. 
    Set autoreload to True to allow reloading once python-files changed.
"""
conf = {
    'global': {
        'server.environment': 'production',
        'engine.autoreload.on': True,
        'engine.autoreload.frequency': 2,
        'server.socket_host': '0.0.0.0',  # Listen on any interface
        'server.socket_port': 8080,
        'tools.encode.text_only': False
        },
    '/': {
        'tools.sessions.on': True,
        'tools.auth.on': True,
        'tools.staticdir.root': os.path.abspath("www/")
    },
    '/static': {
        'tools.auth.on': False,
        'tools.staticdir.on': True,
        'tools.staticdir.dir': '.',
        'tools.caching.on': True,
        'tools.caching.delay': 3600,
        'tools.caching.antistampede_timeout': 1,
        'tools.gzip.on': True,
        'tools.gzip.mime_types': ['text/*', 'application/*']
    },
    '/favicon.ico': {
        'tools.staticfile.on': True,
        'tools.staticfile.dir': os.path.abspath('www/figures/comsys.png')
    }
}

class RestrictedArea:
    
    # all methods in this controller (and subcontrollers) is
    # open only to members of the admin group
    
    _cp_config = {
        'auth.require': [modules.auth.member_of('admin')]
    }
    
    @cherrypy.expose
    def index(self):
        return """This is the admin only area."""

"""
    Global index-class. Maps to root (localhost:8080/).
"""

class cIndex(object):
    
    auth = modules.auth.AuthController()

    machine = cmachine.CoffeeMachine()
    
    restricted = RestrictedArea()

    def __init__(self):
        pass

    #@staticmethod
    #@cherrypy.expose
    #def index(**params):
    #    del params
    #    return serve_file(os.path.abspath('./www/index.html'), 'text/html')
    
    @cherrypy.expose
    @modules.auth.require()
    def index(self):
        return templates.get_template("index.html").render()

gIndex = cIndex()

def webInterface():
    logging.info("Starting Cherrypy-Engine")
    cherrypy.quickstart(gIndex, config=conf)


def shutdown():
    # shut webinterface down
    logging.info("Saving Settings")
    settings.write("config/settings.json")
    logging.info("Shutting down Cherrypy-Engine")
    cherrypy.engine.exit()

"""
    Assumes that cherrypy exists + logging etc is setup.
"""


def run():

    # Suppress cherrypy's logging
    #cherrypy.log.error_log.propagate = False
    cherrypy.log.access_log.propagate = False

    # Execute the prepared settings-file
    # Utilized pythons eval/exec and is therefore not completely save, but allows for great configurability
    settings.read("config/settings.default.json")
    settings.read("config/settings.json")

    #logging.getLogger().setLevel(settings.loglevel)

    conf['global']['server.socket_port'] = settings.webPort


    Thread(target=webInterface).start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        shutdown()
