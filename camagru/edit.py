import os, uuid
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,
    current_app
)
from PIL import Image
from camagru.db import get_db

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

    stickers = []
    if os.path.exists(os.path.join(current_app.root_path, "static", "stickers")):
        stickers = [{ "name": f,
                      "path": os.path.join("/static/stickers", f)}
                      for f in os.listdir(os.path.join(current_app.root_path, "static", "stickers"))]

    posts = []
    if (os.path.exists(os.path.join(current_app.root_path, "static", "posts"))):
        db = get_db()
        cursor = db.execute(
            """
            SELECT * FROM POST
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (g.user["id"],))
        posts_db = cursor.fetchall()
        for post in posts_db:
            posts.append({
                "id": post["id"],
                "path": os.path.join("/static", "posts", post["image_name"]),
                "created_at": post["created_at"].strftime("%Y-%m-%d %H:%M"),
            })

    if request.method == "POST":
        if "image_data" not in request.files:
            flash("No file selected")
            return redirect(url_for("edit.edit"))
        if "sticker_name" not in request.form:
            flash("No sticker selected")
            return redirect(url_for("edit.edit"))

        capture = Image.open(request.files["image_data"])
        sticker = Image.open(os.path.join("camagru/static/stickers", request.form["sticker_name"]))
        final = Image.new("RGBA", (640, 480))
        final.paste(sticker, (0, 0))
        final.paste(capture, (0, 0))

        name = f"{uuid.uuid4().hex[:16]}.png"
        final.save(os.path.join(current_app.root_path, "static", "posts", name))

        user = g.user
        db = get_db()
        db.execute(
            "INSERT INTO POST (user_id, image_name) VALUES (?, ?)",
            (user["id"], name))
        db.commit()
        flash("File saved")
        return redirect(url_for("edit.edit"))

    return render_template("edit/edit.html", stickers=stickers, posts=posts)

@bp.route("/delete/<int:post_deleted>")
def delete(post_deleted=None):
    db = get_db()
    post_db = db.execute("SELECT * FROM POST WHERE id = ?", (post_deleted,)).fetchone()
    if not post_db:
        flash("This post does not exist")
        return redirect(url_for("edit.edit"))
    if not post_db["user_id"] == g.user["id"]:
        flash("You must be the owner of this post to delete it")
        return redirect(url_for("edit.edit"))
    db.execute("DELETE FROM COMMENT WHERE post_id = ?", (post_deleted,))
    db.execute("DELETE FROM HEART WHERE post_id = ?", (post_deleted,))
    db.execute("DELETE FROM POST WHERE id = ?", (post_deleted,))
    db.commit()
    return redirect(url_for("edit.edit"))