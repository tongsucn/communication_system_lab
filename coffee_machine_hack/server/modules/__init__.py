
from mako.template import Template
from mako.lookup import TemplateLookup

templates = TemplateLookup(directories=['www/templates'], module_directory='/tmp/mako_modules')