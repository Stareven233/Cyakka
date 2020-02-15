from flask import render_template, flash
from . import main


@main.app_errorhandler(404)
def page_not_found(e):
    flash('没见过的连接，是新游戏哦？')
    return render_template('error.html', error_code=404), 404


@main.app_errorhandler(403)
def forbidden(e):
    flash('不要，不要啊，别看')
    return render_template('error.html', error_code=403), 403


@main.app_errorhandler(413)
def over_limit(e):
    flash('不行不行，这个太大了')
    return render_template('error.html', error_code=413), 413


@main.app_errorhandler(500)
def over_limit(e):
    flash('已经...坏掉了...')
    return render_template('error.html', error_code=500), 500
