from flask import Flask 
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_uploads import UploadSet, configure_uploads, IMAGES
from jinja2 import Environment
from elasticsearch import Elasticsearch
from flask_socketio import SocketIO, send

app = Flask(__name__)
photos = UploadSet('photos', IMAGES)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/example'
socketio = SocketIO(app)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
jinja_env = Environment(extensions=['jinja2.ext.loopcontrols'])




app.config['UPLOADED_PHOTOS_DEST'] = 'app/static/photos'
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app) #login usuarios manager
login.login_view = 'login'
configure_uploads(app, photos)
app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) if app.config['ELASTICSEARCH_URL'] else None


#app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) if app.config['ELASTICSEARCH_URL'] else None


from app import  routes, models

if __name__ == '__main__':
	socketio.run(app)






