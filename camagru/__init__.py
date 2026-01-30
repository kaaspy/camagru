import os
from flask import Flask, redirect, url_for

def create_app(config=None):
    app = Flask(__name__)

    if config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.from_mapping(config)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(os.path.join(app.root_path, "static", "posts"), exist_ok=True)

    @app.route("/")
    @app.route("/index")
    def index():
        return redirect(url_for("browse.browse"))
    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import edit
    app.register_blueprint(edit.bp)

    from . import browse
    app.register_blueprint(browse.bp)

    @app.context_processor
    def inject():
        return {
            "base_url": app.config["BASE_URL"],
        }

    return app
