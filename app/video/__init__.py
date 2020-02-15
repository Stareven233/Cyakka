from flask import Blueprint

video = Blueprint('video', __name__)

from . import views  # 写后面避免views, errors循环导入
