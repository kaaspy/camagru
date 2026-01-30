from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,
    current_app
)
from camagru.db import get_db
from camagru.file import save_image

bp = Blueprint("edit", __name__, url_prefix="/edit")

@bp.before_app_request
def load_user_session():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM USER WHERE id = ?", (user_id,)
        ).fetchone()

@bp.route("/", methods=("GET", "POST"))
def edit():
    if g.user is None:
        flash("You must be logged in to use the editor")
        return redirect(url_for("auth.login"))
    if not g.user["is_valid"]:
        flash("You must validate your email to use the editor")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        if "uploaded_image" not in request.files:
            flash("No file selected")
            return redirect(url_for("edit.edit"))

        file = request.files["uploaded_image"]
        (is_saved, name) = save_image(file)
        if not is_saved:
            flash(name)
            return redirect(url_for("edit.edit"))

        user = g.user
        db = get_db()
        db.execute(
            "INSERT INTO POST (user_id, image_name) VALUES (?, ?)",
            (user["id"], name))
        db.commit()
        
        flash("File saved")

    return render_template("edit/edit.html")
