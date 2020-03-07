from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(2, 30)])
    # email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def validate_username(self, field):  # 将随着同名字段验证时一起被调用
        self.user = User.query.filter_by(username=field.data).first()
        if not self.user:
            raise ValidationError('用户名不存在')

    def validate_password(self, field):
        if not self.user:
            return None
        if not self.user.verify_password(field.data):
            raise ValidationError('密码错误')


class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(2, 20), Regexp(
                                        r'^[A-Za-z0-9\u4e00-\u9fa5_.]*$', 0, '只能有汉字、拉丁字母、数字及下划线...')])
    email = StringField('邮箱', validators=[DataRequired(), Length(6, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired(), EqualTo('password2', '前后密码不一致')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_username(self, field):  # 将随着同名字段验证时一起被调用
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已注册')
