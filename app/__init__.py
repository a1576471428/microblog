from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from config import basedir

# 网站初始化
app = Flask(__name__)
app.config.from_object('config')

# 用户管理初始化
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

oid = OpenID(app, os.path.join(basedir, 'tmp')) # openid需要一个存储文件的文件夹

# 数据库初始化
db = SQLAlchemy(app)

from app import views, models