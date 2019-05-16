import click
from flask.cli import AppGroup
from thefort.database import db
from flask import current_app
import os
import random
from datetime import datetime

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
    roles = ["admin", "user", "data"]
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


@core_cli.command("import_products")
@click.option("--filename", prompt=True, default="item_dump.csv")
def load_product(filename):
    fn = os.path.join(current_app.instance_path, "data", filename)
    total_counter, update_counter, insert_counter = import_items(fn)
    return total_counter, update_counter, insert_counter


@core_cli.command("random_category")
def random_category():
    c = [x for x in Category.query.all()]
    p = Product.query.filter_by(active=True).all()
    for product in p:
        product.categories.append(random.choice(c))
    db.session.commit()


@core_cli.command("update_categories")
@click.option("--filename", prompt=True, default="data_export.json")
def update_categories(filename):
    """ Updates existing products with categories provided from a .json formatted file

        file formatted as [{'gtin': '000000000000000', categories=['aaaa', 'bbbb'], ...]
        The categories are the `slug` reference to keep things easier for matching.
    """
    fn = os.path.join(current_app.instance_path, "data", filename)
    update_category_to_products(fn)
    click.echo("Categories mapped.")


@core_cli.command("update_descriptions")
@click.option("--filename", prompt=True, default="description_map.json")
def map_categories(filename):
    fn = os.path.join(current_app.instance_path, "data", filename)
    map_description_to_products(fn)
    click.echo("Descriptions updated.")


@core_cli.command("activate_product")
def activate_product():
    db.session.query(Product).update({"active": True})
    db.session.commit()


@core_cli.command("random_unit")
def random_unit():
    c = ["Full Case", "Half Case", "Single"]
    p = Product.query.filter_by(active=True).all()
    for product in p:
        product.unit = random.choice(c)
    db.session.commit()


@core_cli.command("guessed_unit")
def guessed_unit():
    p = Product.query.all()

    for product in p:
        ids = f"{product.id}"
        if len(ids) == 5:
            print(f"Len is 5 for {product}")
            # click.echo('Length Match of 5')
            if ids[0] == "7":
                # click.echo('Updating Each')
                click.echo(f"setting {product} as EACH")
                product.unit = "EACH"
            elif ids[0] == "6":
                # click.echo('Updating Half-Case')
                product.unit = "HALF-CASE"
        else:
            if ids[-1] == "5":
                product.unit = "EACH"

    db.session.commit()
    click.echo("Guessed Units!")
