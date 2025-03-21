from flask.cli import FlaskGroup
from app import create_app, db
from app.models import User, Article, PlatformAccount
import click

cli = FlaskGroup(create_app=create_app)

@cli.command('create-admin')
@click.argument('username')
@click.argument('password')
def create_admin(username, password):
    """创建管理员用户"""
    user = User(username=username, email=f'{username}@admin.com', role='admin')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f'Created admin user: {username}')

@cli.command('init-db')
def init_db():
    """初始化数据库"""
    db.create_all()
    click.echo('Initialized database.')

if __name__ == '__main__':
    cli() 