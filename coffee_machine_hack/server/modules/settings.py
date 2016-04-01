#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
from modules import *
from modules.main import gIndex

"""
    Really convenient but unpythonic way of handling settings implemented here.
    Maps the settings-file to python-code applying the settings and exec's it.
    Allows adding of arbitrary values to the settings, as long as they are available
    during load + save. Load will be executed after all classes are created, and save during shutdown.
    Allows loading multiple setting files (used for settings.default.json), but saving will save to a single
    settings-file.
"""

globalSettings = {}

# Add Default value for global settings here

loglevel = 20
webPort = 8080
product_list = []
coffeCount = 10
cherrypy_config = {}


def read(setFile):
    global globalSettings
    try:
        with open(setFile, "r+") as jsonFile:
            globalSettings.update(json.loads(jsonFile.read()))

            for key in globalSettings.keys():
                val = globalSettings[key]
                if '.' not in key:
                    source = "global " + key + ";\n"
                else:
                    source = ""
                if isinstance(val, int):
                    source += key + "=" + str(val) + "\n"
                elif isinstance(val, str):
                    source += key + "=\"" + val + "\"\n"
                elif isinstance(val, dict):
                    source += key + ".update(" + repr(val) + ")\n"
                else:
                    source += key + "=" + repr(val) + "\n"
                try:
                    exec(source)
                except NameError as e:
                    logging.error('Invalid setting: ' + key)
                    logging.error(e)
    except IOError:
        logging.warning("A config file couldn't be found. If you're running pyRTMF for the first time, this can be ignored.")
    except ValueError as e:
        logging.error(e)
        logging.error("Syntax Error in config File " + setFile + ". Will be overwritten on exit.")


def write(fileName):
    global globalSettings
    if fileName == "":
        logging.error("No Filename given.")
        return
    with open(fileName, 'w') as outfile:
        for key in globalSettings.keys():
            val = eval(key)
            globalSettings[key] = val
        json.dump(globalSettings, outfile, indent=4, sort_keys=True)
