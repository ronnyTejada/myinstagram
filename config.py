import os
from jinja2 import Environment

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
	 'mysql://root:''@localhost/User'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	jinja_env = Environment(extensions=['jinja2.ext.loopcontrols'])
	ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')