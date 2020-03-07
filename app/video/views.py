from flask import render_template, redirect, url_for, request, current_app, abort
from . import video
from .forms import VideoForm
from ..models import Video, Comment, Permission, Log
from .. import db, up_files
from ..decorators import permission_required
from flask_login import current_user, login_required
from os import remove
from datetime import datetime


@video.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = VideoForm()
    if form.validate_on_submit():
        v_file = request.files['video']
        v_face = form.face.data  # 两种方法都可
        max_id = db.session.execute('select max(id) from videos').fetchone()  # '..RowProxy' tuple形式(2,)
        max_num = str((0 if not max_id[0] else max_id[0]) + 1)
        filename = max_num + '.' + v_file.filename.rsplit('.')[1]
        facename = max_num + '.' + v_face.filename.rsplit('.')[1]

        new_video = Video(title=form.title.data,
                          file=filename,
                          author_id=current_user.id,
                          type=form.type.data,
                          face=facename,
                          desc=form.desc.data)  # title=form.title出错
        up_files.save(v_file, name=f'videos/{filename}')
        up_files.save(v_face, name=f'video_faces/{facename}')
        log = Log(uid=current_user.id, op=2, detail=f'av {max_num}')
        db.session.add_all([new_video, log])
        db.session.commit()

        return redirect(url_for('video.manager'))
    return render_template('video/upload.html', form=form)


@video.route('/reload', methods=['POST'])
@login_required
def reload():
    form = VideoForm()
    if form.validate_on_submit():
        av = request.form['av']
        bideo = Video.query.filter_by(id=av).first()
        v_file = form.video.data
        v_face = form.face.data

        if v_file:
            remove(current_app.config['UPLOADED_FILES_DEST'] + 'videos/' + bideo.file)
            bideo.file = str(bideo.id) + '.' + v_file.filename.rsplit('.')[1]
            up_files.save(v_file, name=f'videos/{bideo.file}')
            bideo.like = bideo.coin = bideo.collect = 0
        if v_face:
            remove(current_app.config['UPLOADED_FILES_DEST'] + 'video_faces/' + bideo.face)
            bideo.face = str(bideo.id) + '.' + v_face.filename.rsplit('.')[1]
            up_files.save(v_face, name=f'video_faces/{bideo.face}')

        bideo.title = form.title.data
        bideo.desc = form.desc.data
        bideo.type = form.type.data
        bideo.status = 0  # 需重新审核
        bideo.date = datetime.now()
        log = Log(uid=current_user.id, op=2, detail=f'av {av}')
        db.session.add_all([bideo, log])
        db.session.commit()
    return 'success'


@video.route('/manage', methods=['GET', 'POST'])
@login_required
def manage():
    form = VideoForm()
    if request.method == 'POST':
        av = request.get_data().decode('utf-8')
        v = Video.query.filter_by(id=av).first()
        log = Log(uid=current_user.id, op=4, detail=f'av {av}')
        db.session.add(log)
        db.session.delete(v)
        db.session.commit()
        return 'success'
    # bideo = current_user.videos.all()
    page = request.args.get('page', 1, type=int)
    pagination = current_user.videos.order_by(Video.date.desc()).paginate(
        page=page,
        per_page=current_app.config['CYAKKA_VIDEO_PER_PAGE']
    )
    bideo = pagination.items
    return render_template('video/manage.html', videos=bideo, pagination=pagination, form=form)


@video.route('/<string:v_type>')
def classify(v_type):
    type_tuple = current_app.config['CYAKKA_VIDEO_TYPES'].get(v_type)
    if not type_tuple:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = Video.query.filter_by(type=str(type_tuple[0]), status=1).order_by(Video.date.desc()).paginate(
        page=page,
        per_page=current_app.config['CYAKKA_VIDEO_PER_PAGE']
    )
    bideo = pagination.items
    return render_template('video/divisions.html', v_type=v_type,
                           v_types=current_app.config['CYAKKA_VIDEO_TYPES'],
                           videos=bideo,
                           pagination=pagination)


@video.route('/av<int:av>')
def play(av):
    bideo = Video.query.get_or_404(av)  # 应是完整文件名
    if bideo.status != 1 and not current_user.can(Permission.AUDIT):  # 审核中或者审核未通过需auditor才能看
        abort(404)
    v_type = list(current_app.config['CYAKKA_VIDEO_TYPES'].values())[bideo.type-1][1]

    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (bideo.comments.count() - 1)//current_app.config['CYAKKA_COMM_PER_PAGE'] + 1
    pagination = bideo.comments.order_by(Comment.date.asc()).paginate(
        page=page,
        per_page=current_app.config['CYAKKA_COMM_PER_PAGE'],
        error_out=False
    )
    comms = pagination.items
    return render_template('video/play.html', video=bideo, v_type=v_type, comments=comms, pagination=pagination)


@video.route('/comment', methods=['POST'])
@login_required
@permission_required(Permission.COMMENT)
def comment():
    av = request.args.get('av', type=int)
    bideo = Video.query.get_or_404(av)
    if bideo.status is not 1:
        return 'video status error'

    comm_body = request.get_data()
    comm = Comment(body=comm_body,
                   author=current_user._get_current_object(),
                   video=bideo)
    db.session.add(comm)
    db.session.commit()
    # return redirect(url_for('video.comment', av=av, page=-1))  # -1表示最后一页
    return 'success'


@video.route('/comment/tip', methods=['POST'])
@login_required
@permission_required(Permission.COMMENT)
def tip_comment():
    if request.method == 'POST':
        cid = request.get_data()
        comm = Comment.query.filter_by(id=cid).first()
        if not comm or comm.tipped:
            abort(403)  # 不存在的或已举报
        comm.tipped = True
        comm.tip_user = current_user.id
        db.session.add(comm)
        db.session.commit()
        return 'success'


@video.route('/ops_<string:action>', methods=['POST'])
@login_required
@permission_required(Permission.COMMENT)
def alter_statistic(action):
    if action not in ['like', 'collect', 'coin']:
        return 'action type error'
    light_on = eval(request.form[action].capitalize())  # 当前是否点亮
    av = request.form['av']
    bideo = Video.query.get_or_404(av)

    if bideo.status is not 1:
        return 'video status error'
    # bideo.like += [-1, 1][like]
    if action == 'like' and light_on:
        bideo.like -= 1
        current_user.v_like.remove(bideo)
        log = Log.query.filter(Log.uid == current_user.id, Log.op == 3, Log.detail == f'av {av}').first()
        db.session.delete(log)
    elif action == 'like' and not light_on:
        bideo.like += 1
        current_user.v_like.append(bideo)
        log = Log(uid=current_user.id, op=3, detail=f'av {av}')
        db.session.add(log)
    if action == 'collect' and light_on:
        bideo.collect -= 1
        current_user.v_collect.remove(bideo)
    elif action == 'collect' and not light_on:
        bideo.collect += 1
        current_user.v_collect.append(bideo)
    if action == 'coin' and not light_on and current_user.coins >= 1:
        current_user.coins -= 1
        bideo.coin += 1
        current_user.v_coin.append(bideo)
    elif action == 'coin':
        return 'no refunds or coins run out'

    db.session.add_all([bideo, current_user._get_current_object()])
    db.session.commit()
    return 'success'


@video.route('/is_<string:action>')
def confirm_statistic(action):
    if not current_user.is_authenticated:
        return 'None'  # 装饰器会返回登录html，而非None
    av = request.args.get('av', type=int)
    if action == 'like':
        return current_user.v_like.filter_by(id=av).first().__repr__()
    elif action == 'coin':
        return current_user.v_coin.filter_by(id=av).first().__repr__()
    elif action == 'collect':
        return current_user.v_collect.filter_by(id=av).first().__repr__()
    return 'Error'
