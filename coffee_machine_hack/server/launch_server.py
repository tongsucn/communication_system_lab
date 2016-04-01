#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import os.path
import sys
import logging
from logging import handlers

"""
   =========================
             Main
   =========================
"""

"""
    Verify that we're running python > 3.4 and cherrypy is available.
    We might get away with any Python 3 Version, development + testing happened under 3.4/5 though.
    So just make sure thats available.
"""


def check_python():
    python_Version = sys.version_info
    return python_Version.major >= 3 and python_Version.minor >= 4


def check_cherrypy():
    try:
        __import__("cherrypy")
    except ImportError:
        logging.info("Cherrypy is missing on this system. Please install cherrypy.")
        return False
    import cherrypy
    versParts = cherrypy.__version__.split('.')
    versParts = [int(x) for x in versParts]
    if versParts[0] > 4:
        logging.info("This application was developed with cherrypy v.4.0.0. Currently installed is " +
                     cherrypy.__version__ + ". Full functionality cannot be guaranteed.")
    return True

if __name__ == '__main__':
    # Initializing logging
    # Create log_path
    log_path = './log'
    if not os.path.exists(log_path):
        os.mkdir(log_path)

    # Set root directory to script directory, to allow execution from anywhere
    # (Needs to happen before modules import, since __init__'s of some modules already use relative paths)
    scriptDir = os.path.dirname(sys.argv[0])
    logFile = os.path.join(log_path, 'server.log')
    if scriptDir:
        logging.debug("Setting root dir to " + scriptDir)
        os.chdir(scriptDir)

    logging.info("Opening log-file: " + logFile)

    # Enable + configure logging
    logging.getLogger().setLevel(logging.INFO)

    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-5.5s] [%(levelname)-5.5s] %(funcName)s : %(message)s")
    rootLogger = logging.getLogger()

    # Set the default logger to use our format
    for handler in rootLogger.handlers:
        handler.setFormatter(logFormatter)

    fileHandler = handlers.RotatingFileHandler(logFile, maxBytes=1024*1024*20, backupCount=1)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    if not check_python():
        logging.info("Python 3.4 or newer is required to run this application.")
        sys.exit()

    if not check_cherrypy():
        sys.exit()

    from modules import main
    main.run()
