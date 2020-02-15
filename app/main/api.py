from . import main
from flask import request, jsonify
from flask_login import current_user, login_required
from .. import db
from ..models import Video, Permission, Danmaku
from ..decorators import permission_required
import json


@main.route('/api/danmaku', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.COMMENT)
def danmaku():
    response = {'code': 0, 'data': 'null'}
    if request.method == 'POST':
        payload = json.loads(request.data.decode())

        av = int(payload.get('id'))
        bideo = Video.query.get_or_404(av)
        if not bideo or bideo.status != 1:
            response['code'] = -403
            response['data'] = 'Error: limited video'
            return jsonify(response)

        d = Danmaku(time=payload['time'],
                    text=payload['text'],
                    color=payload['color'],
                    type=payload['type'],
                    author=current_user._get_current_object(),
                    video=bideo)
        db.session.add(d)
        db.session.commit()
        return jsonify(response)

    av = request.args.get('id', type=int)
    danmakus = Danmaku.query.filter_by(video_id=av).all()
    response['data'] = [d.to_dict() for d in danmakus]
    return jsonify(response)
