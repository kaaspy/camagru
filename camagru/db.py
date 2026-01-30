import sqlite3, os
from datetime import datetime

import click
from flask import current_app, g

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as schema:
        db.executescript(schema.read().decode("utf8"))
    posts_path = os.path.join(current_app.root_path, "static", "posts")
    for filename in os.listdir(posts_path):
        path = os.path.join(posts_path, filename)
        try:
            if os.path.isfile(path):
                os.remove(path)
        except Exception as e:
            print(f"Post deletion failed : {path} : {e}")
    try:
        os.removedirs(os.path.join(current_app.root_path, "static", "posts"))
    except Exception as e:
        print(f"Post folder deletion failed : {e}")

@click.command("init-db")
def init_db_command():
    """Clear all data and regenerate tables"""
    init_db()
    click.echo("DB initialized")

sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)