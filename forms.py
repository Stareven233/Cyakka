from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, FileField
from wtforms import widgets, SelectMultipleField, RadioField
from wtforms.validators import DataRequired, Length, Email, Regexp
from flask_wtf.file import FileRequired, FileAllowed
from ..models import User, Perm_choices
from wtforms import ValidationError
from flask_uploads import IMAGES
from config import video_eng_types, video_chi_types


type_choices = list(zip(['users', 'videos'], ['用户', '视频']))
order_choices = list(zip(['all', 'new', 'like', 'collect'], ['综合排序', '最新发布', '最多点赞', '最多收藏']))
div_choices = [('all', '全部分区')] + list(zip(video_eng_types, video_chi_types))
anchor_choices = list(zip(['name', 'id'], ['用户名', 'UID']))  # 用户搜索时专用
op_choices = list(zip(['login', 'like', 'up', 'del'], ['登录记录', '点赞视频', '上传稿件', '删除稿件']))


class LogForm(FlaskForm):
    op = RadioField(coerce=str, choices=op_choices)
    uid = StringField(validators=[DataRequired(), Length(1, 11)])


class SearchForm(FlaskForm):
    keyword = StringField(validators=[Length(1, 50)])
    type = RadioField(coerce=str, choices=type_choices)
    order = RadioField(coerce=str, choices=order_choices)
    div = RadioField(coerce=str, choices=div_choices)
    anchor = RadioField(coerce=str, choices=anchor_choices)


class AvatarForm(FlaskForm):
    avatar = FileField('选择图片', validators=[FileRequired(), FileAllowed(IMAGES)])
    submit = SubmitField('更新')


class AlterAuthForm(FlaskForm):
    # email = StringField('邮箱', validators=[DataRequired(), Length(6, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField('新密码', validators=[DataRequired()])
    submit = SubmitField('修改')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def validate_password(self, field):
        if field.data != self.user.password:
            raise ValidationError('密码错误')

    def validate_password2(self, field):
        if field.data == self.user.password:
            raise ValidationError('与原密码一致')


class ProfileForm(FlaskForm):
    nickname = StringField('昵称', validators=[Length(1, 30, '长度不能超过30个字符')])
    username = StringField('用户名')  # 仅作为展示
    about_me = TextAreaField('个性签名', validators=[Length(0, 60, '长度不能超过60个字符')])
    submit = SubmitField('保存')


class ProfileAdminForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(2, 20), Regexp(
        r'^[A-Za-z0-9\u4e00-\u9fa5_.]*$', 0, '只能有汉字、拉丁字母、数字及下划线...')])
    email = StringField('邮箱', validators=[DataRequired(), Length(6, 64), Email()])
    password = StringField('密码', validators=[DataRequired()])
    nickname = StringField('昵称', validators=[Length(1, 30, '长度不能超过30个字符')])
    permissions = SelectMultipleField(label='权限',
                                      coerce=int,
                                      choices=Perm_choices,
                                      widget=widgets.ListWidget(),
                                      option_widget=widgets.CheckboxInput())
    about_me = TextAreaField('个性签名', validators=[Length(0, 60, '长度不能超过60个字符')])
    submit = SubmitField('保存')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user  # 为了使用user专门设置的init

    def validate_username(self, field):  # 将随着同名字段验证时一起被调用
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')

    def validate_email(self, field):  # 即便是管理员也得不重复才能改用户名/邮箱
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已注册')
