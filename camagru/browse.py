import os, datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,
    current_app, request
)
from camagru.db import get_db
from camagru.mail import comment_mail

PAGE_SIZE = 5

bp = Blueprint("browse", __name__, url_prefix="/browse")

@bp.before_app_request
def load_user_session():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM USER WHERE id = ?", (user_id,)
        ).fetchone()

@bp.context_processor
def processor():
    def show_posts(page):
        posts = []
        if (os.path.exists(os.path.join(current_app.root_path, "static", "posts"))):
            db = get_db()
            cursor = db.execute(
                """
                SELECT * FROM POST
                ORDER BY created_at DESC
                LIMIT ?
                OFFSET ?
                """,
                (PAGE_SIZE, (page - 1) * PAGE_SIZE))
            page = cursor.fetchall()
            users = []
            for post in page:
                if post["user_id"] not in users:
                    user = db.execute("SELECT * FROM USER WHERE id = ?", (post["user_id"],)).fetchone()
                    users.append(user)
                post_creator = next(u for u in users if u["id"] == post["user_id"])

                like_count = db.execute("SELECT COUNT(*) FROM HEART WHERE post_id = ?", (post["id"],)).fetchone()[0]
                comment_count = db.execute("SELECT COUNT(*) FROM COMMENT WHERE post_id = ?", (post["id"],)).fetchone()[0]

                if g.user:
                    is_liked = db.execute("SELECT * FROM HEART WHERE user_id = ? AND post_id = ?", (g.user["id"], post["id"])).fetchone()
                else:
                    is_liked = False

                posts.append({
                    "id": post["id"],
                    "path": os.path.join("/static", "posts", post["image_name"]),
                    "user": "you" if post_creator["id"] == post["user_id"]  else post_creator["username"],
                    "created_at": post["created_at"].strftime("%Y-%m-%d %H:%M"),
                    "like_count": like_count,
                    "comment_count": comment_count,
                    "is_liked": True if is_liked else False,
                })
        return posts
    return dict(show_posts=show_posts)

@bp.route("/")
@bp.route("/<int:page>", methods=("GET", "POST"))
def browse(page=None):
    if not page:
        return redirect(url_for("browse.browse", page=1))

    db = get_db()
    post_number = db.execute("SELECT COUNT(*) FROM POST").fetchone()[0]
    page_number = post_number // PAGE_SIZE + 1
    return render_template("browse/browse.html", page=page, page_number=page_number)

@bp.route("/like/<int:post_liked>")
def like(post_liked=None):
    if not post_liked:
        return redirect(request.referrer)
    user = g.user
    db = get_db()
    is_liked = db.execute("SELECT COUNT(*) FROM HEART WHERE user_id = ? AND post_id = ?",
                            (g.user["id"], post_liked)).fetchone()[0]
    if is_liked:
        flash("You already liked this post")
        return redirect(request.referrer)
    db.execute("INSERT INTO HEART (user_id, post_id) VALUES (?, ?)", (g.user["id"], post_liked))
    db.commit()
    return redirect(request.referrer)

@bp.route("/unlike/<int:post_unliked>")
def unlike(post_unliked=None):
    if not post_unliked or not g.user:
        return redirect(request.referrer)

    db = get_db()
    is_liked = db.execute("SELECT COUNT(*) FROM HEART WHERE user_id = ? AND post_id = ?",
                            (g.user["id"], post_unliked)).fetchone()[0]
    if not is_liked:
        flash("You have not liked this post")
        return redirect(request.referrer)
    db.execute("DELETE FROM HEART WHERE user_id = ? AND post_id = ?", (g.user["id"], post_unliked))
    db.commit()
    return redirect(request.referrer)

@bp.route("/comment/<int:post_commented>", methods=("GET", "POST"))
def comment(post_commented=None):
    if not post_commented:
        return redirect(request.referrer)

    db = get_db()
    post_db = db.execute("SELECT * FROM POST WHERE id = ?", (post_commented,)).fetchone()
    if not post_db:
        flash("This post does not exist")
        return redirect(request.referrer)
    post = {
        "id": post_db["id"],
        "path": os.path.join("/static", "posts", post_db["image_name"]),
    }

    comments = []
    comments_db = db.execute("SELECT * FROM COMMENT WHERE post_id = ?",
                            (post_db["id"],)).fetchall()

    users = []
    for comment in comments_db:
        if comment["user_id"] not in users:
            user = db.execute("SELECT * FROM USER WHERE id = ?", (comment["user_id"],)).fetchone()
            users.append(user)

        comments.append({
            "user": next(u["username"] for u in users if u["id"] == comment["user_id"]),
            "content": comment["content"],
            "created_at": comment["created_at"].strftime("%Y-%m-%d %H:%M"),
        })
    
    if request.method == "POST":
        comment = request.form["comment"]
        if not g.user:
            flash("You must be logged in to comment")
            return redirect(url_for("auth.login"))
        db.execute("INSERT INTO COMMENT (user_id, post_id, content) VALUES (?, ?, ?)", (g.user["id"], post_db["id"], comment))
        db.commit()
        post_creator = db.execute("SELECT * FROM USER WHERE id = ?", (post_db["user_id"],)).fetchone()
        if post_creator["is_notified"] and post_creator["id"] != g.user["id"]:
            comment_mail(post_creator["username"], g.user["username"], post_creator["email"], post_db["id"])
        return redirect(url_for("browse.comment", post_commented=post_commented))

    return render_template("browse/comment.html", post=post, comments=comments)