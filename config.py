from os.path import dirname, sep
from os import urandom, getenv

video_eng_types = ['douga', 'anime', 'music', 'dance', 'movie', 'kichiku', 'game', 'ent', 'life']
video_chi_types = ['动画', '番剧', '音乐', '舞蹈', '电影', '鬼畜', '游戏', '娱乐', '生活']
video_selects = list(zip(range(1, len(video_chi_types)+1), video_chi_types))
video_types = {k: v for k, v in list(zip(video_eng_types, video_selects))}


class Config(object):
    SECRET_KEY = f'aka{urandom(24)}'
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://root:{getenv("DATABASE_PW")}@localhost:3306/cyakka'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADED_FILES_DEST = dirname(__file__)+sep+'app'+sep+'static'+sep
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024
    CYAKKA_VIDEO_TYPES = video_types
    CYAKKA_VIDEO_PER_PAGE = 10
    CYAKKA_COMM_PER_PAGE = 6
    JSON_AS_ASCII = False
    REDIS_URL = {'host': 'localhost', 'port': 6379, 'password': getenv('DATABASE_PW')}

# Mysql mysql://username:password@hostname/database 默认用mysqldb，导致No module named 'MySQLdb'
