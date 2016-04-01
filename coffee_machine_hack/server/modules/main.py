#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import cherrypy
import modules
from modules import users
from modules import templates
from modules import cupdetection

"""
    Add headers for more secure page-rendering
    https://cherrypy.readthedocs.org/en/3.3.0/progguide/security.html
"""


def secureheaders():
    headers = cherrypy.response.headers
    headers['X-Frame-Options'] = 'DENY'
    headers['X-XSS-Protection'] = '1; mode=block'
    headers['Content-Security-Policy'] = "default-src='self'"

cherrypy.tools.secureheaders = \
    cherrypy.Tool('before_finalize', secureheaders, priority=60)

"""
    Global index-class. Maps to root (localhost:8080/).
"""


class cIndex(object):
    auth = modules.users.AuthController()
    detector = cupdetection.cupDetector()

    def __init__(self):
        try:
            from modules import cmachine
        except ImportError as e:
        #if 1:
            from modules import cmachine_debug as cmachine
            logging.warning("Couldn't import coffee-machine. Replacing with debug mockup.")
            logging.warning(e)
        self.machine = cmachine.CoffeeMachine()

    @cherrypy.expose
    @modules.users.require()
    def index(self):
        """ Main webApps the user will interface with """
        return templates.get_template("index.html").render()

    @cherrypy.expose
    @modules.users.require(modules.users.member_of("admin"))
    def debug(self):
        """ Debugging-page for cup-detection. Only available to admins. """
        return templates.get_template("detector_debug.html").render()

    def serverMain(self, cherrypy_config):
        """
            Main Server-function. Blocks until a KeyboardInterrupt is triggered (using Strg + C).
            Handles both Server-start + system shutdown
        """
        logging.info('Starting cherrypy-server')
        cherrypy_config['/']['tools.staticdir.root'] = os.path.abspath("./www")
        try:
            cherrypy.quickstart(self, config=cherrypy_config)
        except KeyboardInterrupt:
            logging.info('Terminated main-thread')

"""
    Main function actually starting the system
    Assumes that cherrypy exists, python is >3.4 + logging etc is setup.
"""


def run():
    global gIndex
    # Suppress cherrypy's logging
    cherrypy.log.error_log.propagate = False
    cherrypy.log.access_log.propagate = False
    cherrypy.log.screen = False

    gIndex = cIndex()
    # Execute the prepared settings-file
    # Utilizes pythons eval/exec and is therefore not completely save, but allows for great configurability
    from modules import settings
    settings.read("config/settings.default.json")
    settings.read("config/settings.json")

    gIndex.machine.update_product_list(settings.product_list)

    gIndex.detector.initializeCamera()

    logging.getLogger().setLevel(settings.loglevel)

    gIndex.serverMain(settings.cherrypy_config)

    # if serverMain exits the system should shut-down
    # Notify all subsystems
    logging.info("Saving Settings")
    settings.write("config/settings.json")
    gIndex.detector.shutdown()
    gIndex.machine.shutdown()
    logging.info("Shutting down Cherrypy-Engine")
    cherrypy.engine.exit()
