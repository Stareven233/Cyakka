from flask import render_template, flash, redirect, url_for, request, current_app, abort, jsonify
from . import main
from ..decorators import admin_required, permission_required
from ..models import User, Video, Permission, Comment, Perm_choices, Log, Log_ops
from .forms import ProfileForm, ProfileAdminForm, AvatarForm, AlterAuthForm, SearchForm, LogForm
from flask_login import current_user, login_required
from .. import db, up_files, redis_db
from os import remove
from sqlalchemy import func


@main.route('/')
def index():
    v_types = current_app.config['CYAKKA_VIDEO_TYPES']
    v_divs = dict()
    div = request.args.get('div', type=str)

    if div in v_types.keys():
        videos = Video.query.filter_by(type=v_types[div][0], status=1).order_by(func.rand()).limit(10)
        return render_template('_indexshows.html', v_divs=videos)

    # for i in range(1, len(v_types)+1):
    for k, v in v_types.items():
        v_divs[k] = Video.query.filter_by(type=v[0], status=1).order_by(func.rand()).limit(10)
    return render_template('index.html', v_divs=v_divs, v_types=v_types)


@main.route('/space/<int:uid>')
def user_space(uid):
    user = User.query.filter_by(id=uid).first_or_404()
    div = request.args.get('div', type=str)
    page = request.args.get('page', 1, type=int)
    up = Video.query.filter_by(author_id=user.id, status=1)
    coll = user.v_collect

    if div not in ['upload', 'collect']:   # 当作请求主页
        videos = dict()
        videos['upload'] = up.order_by(Video.date.desc()).limit(10)
        videos['collect'] = coll.order_by(Video.date.desc()).limit(10)
        return render_template('main/space.html', user=user, videos=videos)
    else:
        query = [up, coll][div == 'collect']
        pagination = query.order_by(Video.date.desc()).paginate(
            page=page,
            per_page=current_app.config['CYAKKA_VIDEO_PER_PAGE']
        )
        return render_template('main/_spaceshow.html', videos=pagination.items,
                               uid=user.id, v_div=div, pagination=pagination)


@main.route('/search')
def search():
    form = SearchForm()
    keyword = request.args.get('keyword')
    if not keyword:
        return render_template('main/search.html', form=form)

    s_type = request.args.get('type', 'videos')
    s_order = request.args.get('order', 'all')
    s_div = request.args.get('div', 'all')
    s_anchor = request.args.get('anchor', 'name')
    page = request.args.get('page', 1, type=int)
    model = [User, Video][s_type == 'videos']
    query = model.query

    if s_type == 'videos':
        form.order.data = s_order
        form.div.data = s_div

        for kw in keyword.split():
            query = query.filter(model.title.contains(kw))

        if s_order == 'new':
            query = query.order_by(model.date.desc())
        elif s_order == 'like':
            query = query.order_by(model.like.desc())
        elif s_order == 'collect':
            query = query.order_by(model.collect.desc())
        elif s_order == 'all':
            query = query.order_by(model.like.desc(), model.collect.desc(), model.date.desc())
            # 排序结果与三参数相对位置有关
        if s_div != 'all':
            query = query.filter_by(type=current_app.config['CYAKKA_VIDEO_TYPES'][s_div][0])
        query = query.filter_by(status=1)

    elif s_type == 'users':
        form.anchor.data = s_anchor

        if s_anchor == 'name':
            for kw in keyword.split():
                query = query.filter(model.nickname.contains(kw))
        elif s_anchor == 'id':
            try:
                uid = int(keyword)
            except ValueError:
                uid = 0  # 不存在的id
            query = query.filter(model.id == uid)

    pagination = query.paginate(
        page=page,
        per_page=current_app.config['CYAKKA_VIDEO_PER_PAGE']
    )
    items = dict()
    items[s_type] = pagination.items or 'nil'
    form.keyword.data = keyword
    form.type.data = s_type
    return render_template('main/search.html', form=form, pagination=pagination, **items)


@main.route('/search/history', methods=['GET', 'POST', 'DELETE'])
def search_history():
    if current_user.is_anonymous:
        key = 'search_history_anonymous'
    else:
        key = f'search_history_{current_user.id}'
    response = dict()
    kw = request.form.get('keyword', '')

    if request.method == 'POST':
        redis_db.lrem(key, 0, kw)  # 删除所有值为kw的记录(若有)
        redis_db.lpush(key, kw)  # 再将kw插入顶部
        redis_db.ltrim(key, 0, 5)  # 仅保留6条记录(区间0-5)
        return 'finish'

    if request.method == 'DELETE':
        redis_db.lrem(key, 0, kw)
        return 'success'

    history = [x.decode() for x in redis_db.lrange(key, 0, 5)]
    response['history'] = history
    return jsonify(response)


@main.route('/back/log-user')
@admin_required
def log_user():
    form = LogForm()
    uid = request.args.get('uid', type=int)
    op = request.args.get('op')
    page = request.args.get('page', 1, type=int)
    if not uid or not op:
        return render_template('main/log_user.html', form=form)

    pagination = Log.query.filter(Log.uid == uid, Log.op == Log_ops.index(op)).paginate(
        page=page,
        per_page=current_app.config['CYAKKA_VIDEO_PER_PAGE']
    )
    form.uid.data = uid
    form.op.data = op
    logs = pagination.items
    return render_template('main/log_user.html', form=form, logs=logs, pagination=pagination)


@main.route('/back/log-admin')
@admin_required
def log_admin():
    op = request.args.get('op')
    page = request.args.get('page', 1, type=int)
    if not op or op not in ['login', 'edit', 'audit', 'register']:
        return render_template('main/log_admin.html')

    if op == 'login' or op == 'edit':
        query = Log.query.filter(Log.op == Log_ops.index(op)).order_by(Log.date.desc())
    elif op == 'audit':
        query = Video.query.filter(Video.status != 0).order_by(Video.date.desc())  # 审核过的
    else:
        query = User.query.order_by(User.member_since.desc())

    pagination = query.paginate(
        page=page,
        per_page=current_app.config['CYAKKA_VIDEO_PER_PAGE']
    )
    items = pagination.items
    return render_template('main/log_admin.html', logs=items, op=op, pagination=pagination)


# 若 "/back/audit/video之类的三级path会导致继承来的样式中用到相对路径的失效
@main.route('/back/audit-video', methods=['GET', 'POST'])
@permission_required(Permission.AUDIT)
def audit_video():
    if request.method == 'POST':
        av = request.form['av']
        status = int(request.form['status'])
        v = Video.query.filter_by(id=av).first()
        v.status = status
        v.inspector = current_user.id
        db.session.add(v)
        db.session.commit()
        return 'success'
    page = request.args.get('page', 1, type=int)
    pagination = Video.query.filter_by(status=0).paginate(
        page=page,
        per_page=current_app.config['CYAKKA_VIDEO_PER_PAGE']
    )
    bideo = pagination.items
    return render_template('main/video_audit.html', videos=bideo, pagination=pagination)


@main.route('/back/audit-comment', methods=['GET', 'POST'])
@permission_required(Permission.AUDIT)
def audit_comment():
    if request.method == 'POST':
        cid = request.form['cid']
        op = request.form['op']
        comm = Comment.query.filter_by(id=cid).first()
        if op == '0':  # 禁言发言者
            db.session.delete(comm)
            comm.author.permissions &= ~Permission.COMMENT
        elif op == '1':  # 禁言(第一个)举报者
            comm.tipped = False
            db.session.add(comm)
            tip_user = User.query.filter_by(id=comm.tip_user).first()
            tip_user.permissions &= ~Permission.COMMENT
        db.session.commit()
        return 'finish'
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.filter_by(tipped=True).paginate(
        page=page,
        per_page=current_app.config['CYAKKA_COMM_PER_PAGE']
    )
    comm = pagination.items
    return render_template('main/comm_manage.html', comments=comm, pagination=pagination)


@main.route('/back/audit-user', methods=['GET', 'POST'])
@permission_required(Permission.ADMIN)
def audit_user():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.member_since.asc()).paginate(
        page=page,
        per_page=current_app.config['CYAKKA_VIDEO_PER_PAGE']
    )
    users = pagination.items
    return render_template('main/user_manage.html', users=users, pagination=pagination)


@main.route('/edit/password', methods=['GET', 'POST'])
@login_required
def edit_password():
    form = AlterAuthForm(user=current_user)
    if form.validate_on_submit():
        current_user.password = form.password2.data
        db.session.add(current_user._get_current_object())  # current.user似乎是包装后的对象
        db.session.commit()
        flash('修改成功')
        return redirect(url_for('.user_space', uid=current_user.id))
    return render_template('main/edit_password.html', form=form)


@main.route('/edit/avatar', methods=['GET', 'POST'])
@login_required
def edit_avatar():
    form = AvatarForm()
    if form.validate_on_submit():
        avatar = request.files['avatar']  # avatar为文件字段的name属性值
        ext = avatar.filename.rsplit('.')[1]
        filename = f'{current_user.id}.' + ext

        if up_files.file_allowed(avatar, ext):
            abort(413)
        if current_user.avatar:
            remove(current_app.config['UPLOADED_FILES_DEST'] + 'avatars/' + current_user.avatar)

        up_files.save(avatar, name=f'avatars/{filename}')
        current_user.avatar = filename
        db.session.add(current_user._get_current_object())
        db.session.commit()
        return redirect(url_for('.user_space', uid=current_user.id))
    return render_template('main/upload_avatar.html', form=form)


@main.route('/edit/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.nickname = form.nickname.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())  # current.user似乎是包装后的对象
        db.session.commit()
        flash('保存成功')
        return redirect(url_for('.user_space', uid=current_user.id))
    form.nickname.data = current_user.nickname
    form.username.data = current_user.username
    form.about_me.data = current_user.about_me
    return render_template('main/edit_profile.html', form=form)


@main.route('/edit/profile<int:uid>', methods=['GET', 'POST'])
@login_required
@admin_required  # 多个装饰器按照执行先后从上到下
def edit_profile_admin(uid):
    user = User.query.get_or_404(uid)
    form = ProfileAdminForm(user=user)

    if form.validate_on_submit():
        log_detail = ''
        if user.username != form.username.data:
            user.username = form.username.data
            log_detail += 'name '
        if user.password != form.password.data:
            user.password = form.password.data
            log_detail += 'pw '
        if user.email != form.email.data:
            user.email = form.email.data
            log_detail += 'email '
        if user.nickname != form.nickname.data:
            user.nickname = form.nickname.data
            log_detail += 'nickname '
        if user.about_me != form.about_me.data:
            user.about_me = form.about_me.data
            log_detail += 'about '
        if user.permissions != sum(form.permissions.data):
            user.permissions = sum(form.permissions.data)  # []默认为0
            log_detail += 'perm '

        if not log_detail:
            return redirect(url_for('.user_space', uid=uid))
        log = Log(uid=current_user.id, op=5, detail=f'UID {user.id}: {log_detail}')
        db.session.add_all([user, log])
        db.session.commit()
        flash('用户信息已修改')
        return redirect(url_for('.user_space', uid=uid))

    form.username.data = user.username
    form.password.data = user.password
    form.email.data = user.email
    form.nickname.data = user.nickname
    form.about_me.data = user.about_me
    user_permission = [p[0] for p in Perm_choices if p[0] & user.permissions]
    form.permissions.process_formdata(user_permission)
    return render_template('main/edit_profile_admin.html', form=form, user=user)
