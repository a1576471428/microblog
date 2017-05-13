from flask.ext.script import Manager
from app import app
from app import db
from flask.ext.migrate import Migrate, MigrateCommand


manager = Manager(app)
migrate = Migrate(app, db)  
manager.add_command('db', MigrateCommand)
'''三步走：1.db init 来创建迁移仓库
           2.db migrate -m "initial migration"来创建迁移脚本, 在数据库结构有变动后创建迁移脚本
           3.db upgrade 来更新数据库'''
if __name__ == '__main__':
    manager.run()