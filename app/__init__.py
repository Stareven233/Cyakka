from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_uploads import UploadSet, configure_uploads, IMAGES
from redis import Redis


class ConflictUpSet(UploadSet):
    def resolve_conflict(self, target_folder, basename):
        return basename  # 保存同名文件时直接覆盖


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
bootstrap = Bootstrap()
up_files = ConflictUpSet(name='FILES', extensions=IMAGES + ('mp4',))  # 设置config的UPLOADED_FILES_ALLOW无效
# ['mp4'].extend(IMAGES) 为None!! 大概是extend需要变量存储结果
redis_db = Redis(**Config.REDIS_URL)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    configure_uploads(app, up_files)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/')
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    from .video import video as video_blueprint
    app.register_blueprint(video_blueprint, url_prefix='/video')
    return app


def create_db_table(app):
    with app.app_context():
        db.create_all()
        # db.create_all() 将寻找所有db.Model的子类，然后在数据库中创建对应的表，已有表就不需要运行
