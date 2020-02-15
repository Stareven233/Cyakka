from . import db
from .models import User, Video
from random import randint
from faker import Faker
from config import video_types


def videos(count):
    fakes = [Faker(locale='zh_CN'), Faker(locale='en_US'), Faker(locale='ja_JP')]
    user_count = User.query.count()
    for i in range(count):
        fake = fakes[randint(0, len(fakes)-1)]
        u = User.query.offset(randint(0, user_count - 2)).first()
        v = Video(title=fake.sentence(nb_words=randint(2, 14))[:32],
                  file=fake.file_name(category=None, extension='mp4'),
                  author=u,
                  type=randint(1, 3),
                  face="default.jpg",
                  desc="")
        db.session.add(v)
    db.session.commit()


def inspector():
    video = Video.query.filter(Video.status != 0).all()
    for v in video:
        v.inspector = randint(1, 3)
        db.session.add(v)
    db.session.commit()


def create_fake_data(app, count=40):
    with app.app_context():
        inspector()
