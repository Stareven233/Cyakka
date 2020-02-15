from app import db
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from Cyakka import app
"""
先激活虚拟环境，因为虚拟环境才有所需模块
再切到 manage.py 所在目录并打开数据库
python manage.py db init：初始化了迁移脚本的环境，生成migrations目录，仅第一次使用需要。
python manage.py db migrate：改变ORM模型后执行，自动在/migrations/versions内生成迁移文件，并在数据库中生成version表。
python manage.py db upgrade：迁移文件!检查无误!后执行，将迁移数据库

ERROR [root] Error: Target database is not up to date (db migrate出现)
① 将alembic_version表的num设为versions文件夹中所需执行的迁移文件名
② 直接删掉versions中的文件...
"""
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
