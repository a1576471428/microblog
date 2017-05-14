from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from .forms import LoginForm , EditForm
from .models import User
from datetime import datetime

# index view function suppressed for brevity



@app.route('/')
@app.route('/index')
#首先，我们添加了 login_required 装饰器。这确保了这页只被已经登录的用户看到。
#另外一个变化就是我们把 g.user 传入给模版，代替之前使用的伪造对象。
@login_required
def index():
    user = g.user
    posts = [
        {
            'author': { 'nickname': 'John' },
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': { 'nickname': 'Susan' },
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html',
        title = 'Home',
        user = user,
        posts = posts)


@app.route('/login', methods=['GET', 'POST'])
#oid.loginhandle 告诉 Flask-OpenID 这是我们的登录视图函数
@oid.loginhandler
def login():
    #Flask 中的 g 全局变量是一个在请求生命周期中用来存储和共享数据。
    # 我敢肯定你猜到了，我们将登录的用户存储在这里(g)。
    if g.user is not None and g.user.is_authenticated:#是认证用户，不必二次登录
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        #lask.session 提供了一个更加复杂的服务对于存储和共享数据。一旦数据存储在会话对象中，
        # 在来自同一客户端的现在和任何以后的请求都是可用的。数据保持在会话中直到会话被明确地删除。
        # 为了实现这个，Flask 为我们应用程序中每一个客户端设置不同的会话文件。
        session['remember_me'] = form.remember_me.data #内容提供器，保存来自同一个客户端的信息
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('login.html',
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])


#登陆后就会回调这个函数
@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "": #登陆失败
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    #接下来，我们从数据库中搜索邮箱地址。如果邮箱地址不在数据库中，
    # 我们认为是一个新用户，因为我们会添加一个新用户到数据库。注意例子中
    # 我们处理空的或者没有提供的 nickname 方式，因为一些 OpenID 提供商可能没有它的信息。
    print('login in : %s' % resp.nickname)
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(nickname=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit() #添加新用户
    remember_me = False
    if 'remember_me' in session:
        #接着，我们从 flask 会话中加载 remember_me 值，这是一个布尔值，我们在登录视图函数中存储的。
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    # 然后，为了注册这个有效的登录，我们调用 Flask-Login 的 login_user 函数。
    login_user(user, remember = remember_me)
    #最后，如果在 next 页没有提供的情况下，我们会重定向到首页，否则会重定向到 next 页。
    return redirect(request.args.get('next') or url_for('index'))


#如果你观察仔细的话，你会记得在登录视图函数中我们检查 g.user
# 为了决定用户是否已经登录。为了实现这个我们用 Flask 的
# before_request 装饰器。任何使用了 before_request 装饰器的函数在接收请求之前都会运行。
#  因此这就是我们设置我们 g.user 的地方:

@app.before_request
def before_request():
    #这就是所有需要做的。全局变量 current_user 是被 Flask-Login 设置的，
    # 因此我们只需要把它赋给 g.user ，让访问起来更方便。有了这个，所有请求将会访问到登录用户，即使在模版里。
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()



# 我们必须编写一个函数用于从数据库加载用户
@lm.user_loader
def load_user(id):
    #请注意在 Flask-Login 中的用户 ids 永远是 unicode 字符串，
    # 因此在我们把 id 发送给 Flask-SQLAlchemy 之前，把 id 转成整型是必须的，否则会报错！
    return User.query.get(int(id))


#登出
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html',
                           user=user,
                           posts=posts)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)