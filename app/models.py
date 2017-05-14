
from hashlib import md5
from app import db #db是在app/__init__.py生成的关联后的SQLAlchemy实例

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), unique = True)
    email = db.Column(db.String(120), unique = True)
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)

# is_authenticated 方法有一个具有迷惑性的名称。一般而言，这个方法应该只返回 True，除非表示用户的对象因为某些原因不允许被认证。
    @property
    def is_authenticated(self) :
        return True

# is_active 方法应该返回 True，除非是用户是无效的，比如因为他们的账号是被禁止。
    @property
    def is_active(self) :
        return True

# is_anonymous 方法应该返回 False，除非是伪造的用户。
    @property
    def is_anonymous(self) :
        return False

# get_id 方法应该返回一个用户唯一的标识符
    def get_id(self):
  #      try:
 #           return unicode(self.id)  # python 2
 #       except NameError:
        return str(self.id)  # python 3

    def avatar(self , size) :
        """
        使用Gravatar服务来进行头像管理
        :param size: 
        :return: 
        """
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest() , size)

    def __repr__(self):
        return '<User %r>' % (self.nickname)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)


'''
class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(320), unique=True)
    password = db.Column(db.String(32), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username
'''