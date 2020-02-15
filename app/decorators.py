from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission


def permission_required(permission):
    def decorator(func):
        @wraps(func)  # 保证被装饰的函数__name__等私有属性不变
        def decorated_func(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)  # 即HTTP禁止错误
            return func(*args, **kwargs)
        return decorated_func
    return decorator  # 需要参数"权限"，故多一层


def admin_required(func):
    return permission_required(Permission.ADMIN)(func)
