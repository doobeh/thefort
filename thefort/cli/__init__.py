import click
from flask.cli import AppGroup
from thefort.database import db
from flask import current_app
import os
import random
from datetime import datetime
from thefort.models import User, Role

core_cli = AppGroup("core")
user_cli = AppGroup("user")
db_cli = AppGroup("db")


@db_cli.command("nuke")
def nuke():
    db.drop_all()


@core_cli.command("init")
def app_init():
    # create instance directory if it doesn't already exist:
    if not os.path.exists(current_app.instance_path):
        os.makedirs(current_app.instance_path)
        print("[x] Created instance folder")
    db.create_all()
    print("[x] Created database")
    roles = ["admin", "user"]
    for role in roles:
        r = Role(role)
        db.session.add(r)
        db.session.commit()
    print("App is ready to launch. Run `flask run` to start a production server.")


@user_cli.command("create")
@click.option("--username", prompt="enter username")
@click.password_option()
def user_create(username, password):
    # Lets check if the user exists already:
    u = User.query.filter_by(username=username).first()
    if u:
        return print("User Already Exists")
    u = User(username=username, password=password)
    u.email = username
    u.active = True
    u.confirmed_at = datetime.now()

    db.session.add(u)
    db.session.commit()

    return print(f"User {u} created")


@user_cli.command("assign")
@click.argument("username")
@click.argument("role")
def assign_user(username, role):
    u = User.query.filter_by(username=username).first()
    if not u:
        click.echo("User Not Found")
        click.Abort()
    r = Role.query.filter_by(name=role).first()
    if not r:
        click.echo("Role Not Found")
        click.Abort()
    if r in u.roles:
        click.echo(f"Role already assigned to {username}")
    else:
        u.roles.append(r)
        db.session.commit()
        click.echo(f"Role {r} assigned to {u}")


@user_cli.command("list")
def user_list_all():
    users = [f"    * {x!r}" for x in User.query.all()]
    return print("\n".join(users))
