from flask import Blueprint
from ..models import Permission

main = Blueprint('main', __name__)


@main.app_context_processor  # 上下文处理器，使Permission能在模板中使用
def inject_permissions():
    return dict(Permission=Permission)


from . import views, errors, api  # 写后面避免views, errors循环导入
