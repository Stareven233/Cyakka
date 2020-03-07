from .forms import LoginForm, RegistrationForm
from . import auth
from ..models import User, Log
from .. import db
from flask import redirect, url_for, render_template, flash, request
from flask_login import login_user, logout_user, login_required, current_user


@auth.route('/login', methods=['GET', 'POST'])
def login():  # 见8.4.5
    form = LoginForm()
    if form.validate_on_submit():
        user = form.user
        if not user.permissions:  # 被封号的不许登录
            flash('啊？你被封号了！')
            return url_for('auth.login')

        login_user(user, form.remember_me.data)  # 8.4.5写入cookie以记住账号
        log = Log(uid=user.id, op=1, detail=request.form.get('ip', 'null'))
        db.session.add(log)
        db.session.commit()

        pre_url = request.args.get('next')  # 因login_required而被跳转的url
        if pre_url is None or not pre_url.startswith('/'):
            pre_url = url_for('main.index')
        return pre_url
    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    password=form.password.data,
                    email=form.email.data,
                    nickname=form.username.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('成功登出')
    return redirect(url_for('main.index'))


@auth.before_app_request
def fresh_last_seen():  # 每次请求后都刷新最后访问时间
    if current_user.is_authenticated:
        current_user.ping()
