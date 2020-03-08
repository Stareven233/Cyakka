from . import db
from sqlalchemy import Column, String, Integer, Boolean, TEXT, DateTime, ForeignKey, SmallInteger, Float
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from datetime import datetime


class Danmaku(db.Model):
    __tablename__ = "danmaku"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, index=True, default=datetime.now)
    time = Column(Float, nullable=False)
    text = Column(db.Text, nullable=False)
    color = Column(Integer, nullable=False)  # 将#颜色以十进制形式存储
    type = Column(SmallInteger, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'))
    video_id = Column(Integer, ForeignKey('videos.id'))

    def to_dict(self):
        return [self.time, self.type, self.color, self.author.username, self.text]


class Log(db.Model):
    __tablename__ = "log"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, index=True, default=datetime.now)
    uid = Column(Integer)
    op = Column(SmallInteger)  # 1-5: {(用户)登录、[上传、点赞、删除(视频)]} {(管理)修改(用户信息)}
    detail = Column(String(64))


Log_ops = ['placeholder', 'login', 'up', 'like', 'del', 'edit']


class Comment(db.Model):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    body = Column(db.Text, nullable=False)
    date = Column(DateTime, index=True, default=datetime.now)
    disabled = Column(Boolean)
    author_id = Column(Integer, ForeignKey('users.id'))
    video_id = Column(Integer, ForeignKey('videos.id'))
    tipped = Column(Boolean)
    tip_user = Column(Integer)  # 举报该评论的用户


class Video(db.Model):
    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True)
    title = Column(String(32))
    file = Column(String(20), default="")
    date = Column(DateTime, index=True, default=datetime.now)  # datetime.now是函数对象
    author_id = Column(Integer, ForeignKey('users.id'))  # 外键应绑定表名而非类名
    type = Column(SmallInteger, index=True)
    face = Column(String(20), default="")
    desc = Column(String(64))
    comments = db.relationship('Comment', backref='video', lazy='dynamic')
    like = Column(Integer, default=0, index=True)
    coin = Column(Integer, default=0, index=True)
    collect = Column(Integer, default=0, index=True)
    status = Column(SmallInteger, default=0)  # 审核中，通过，未通过
    inspector = Column(Integer, default=0)
    danmaku = db.relationship('Danmaku', backref='video', lazy='dynamic')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


v_likes = db.Table('v_likes', Column('user_id', Integer, db.ForeignKey('users.id')), Column('video_id', Integer, db.ForeignKey('videos.id')))
v_coins = db.Table('v_coins', Column('user_id', Integer, db.ForeignKey('users.id')), Column('video_id', Integer, db.ForeignKey('videos.id')))
v_collects = db.Table('v_collects', Column('user_id', Integer, db.ForeignKey('users.id')), Column('video_id', Integer, db.ForeignKey('videos.id')))
# 关联表r; u -> v：多->多; u,v -> r： 一->多


class Permission:
    LOGIN = 1  # 登录/关注..
    COMMENT = 2  # 点赞,评论..
    VIP = 4  # 大会员，暂无
    AUDIT = 8  # 审核
    ADMIN = 16  # 管理


Perm_choices = [(v, k) for k, v in Permission.__dict__.items() if not k.startswith('__')]


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(16), unique=True, index=True)
    password = Column(String(32))  # unique似乎是sqlalchemy才有的
    email = Column(String(32), unique=True, index=True)
    avatar = Column(String(20), default="")  # 保存头像文件名，包括后缀
    nickname = Column(String(16))
    about_me = Column(TEXT(), default='')
    member_since = Column(DateTime(), default=datetime.now)
    last_seen = Column(DateTime(), default=datetime.now)
    videos = db.relationship('Video', backref='author', lazy='dynamic')  # user.videos返回查询对象而非结果
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    v_like = db.relationship('Video', secondary=v_likes, backref='liked', lazy='dynamic')
    v_coin = db.relationship('Video', secondary=v_coins, backref='coined', lazy='dynamic')
    v_collect = db.relationship('Video', secondary=v_collects, backref='collected', lazy='dynamic')
    permissions = Column(Integer, default=3)
    danmaku = db.relationship('Danmaku', backref='author', lazy='dynamic')
    coins = db.Column(Integer, default=0)
    # 不存在/封禁0, 普通会员(关注1 弹幕,评论2..)3, 大会员(还没想好4), 审核(稿件,评论8), 管理员(用户密码邮件更改,封号16)

    def __init__(self, **kwargs):  # 原理不明...
        super().__init__(**kwargs)

    def verify_password(self, password):
        if password == self.password:
            return True
        return False

    def ping(self):  # 刷新用户最后访问时间
        now = datetime.now()
        if now.day != self.last_seen.day or (now - self.last_seen).days > 0:
            self.coins += 1
        self.last_seen = now
        db.session.add(self)
        db.session.commit()

    def can(self, perm):
        return self.permissions & perm

    def is_administrator(self):
        return self.can(Permission.ADMIN)


class AnonymousUser(AnonymousUserMixin):
    def can(self, perm):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
