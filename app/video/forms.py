from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, StringField, SelectField
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.validators import DataRequired, Length, NumberRange
from flask_uploads import IMAGES
from config import video_selects


class VideoForm(FlaskForm):
    video = FileField('视频', validators=[FileRequired(), FileAllowed(['mp4'])])  # gif仅用于测试
    title = StringField('标题', validators=[DataRequired('请输入标题'), Length(2, 31)])
    face = FileField('封面', validators=[FileRequired(), FileAllowed(IMAGES)])
    desc = StringField('简介', validators=[Length(0, 63)])
    type = SelectField(label='分区',
                       coerce=int,
                       choices=video_selects,
                       validators=[DataRequired('请选择分区')])
    submit = SubmitField('上传')
