import functools, secrets

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,
    current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
from camagru.db import get_db
from camagru.mail import registration_mail, recovery_mail

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.before_app_request
def load_user_session():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM USER WHERE id = ?", (user_id,)
        ).fetchone()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view

@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        db = get_db()
        error = None

        if not username:
            error = "Username is required"
        if not email:
            error = "Email is required"
        if not password:
            error = "Password is required"
        
        strength = 0
        special_chars = "!@#$%^&*(),.?\":{}|<>"
        if len(password) >= 8:
            strength += 1
        if any(c.isupper() for c in password):
            strength += 1
        if any(c.islower() for c in password):
            strength += 1
        if any(c.isdigit() for c in password):
            strength += 1
        if any(c in special_chars for c in password):
            strength += 1
        
        if strength < 3:
            error = "Your password is too weak"

        if error is None:
            token = secrets.token_urlsafe(16)
            try:
                db.execute(
                    "INSERT INTO USER (username, email, password, token) VALUES (?, ?, ?, ?)",
                    (username, email, generate_password_hash(password), token)
                )
                db.commit()
            except db.IntegrityError as e:
                if "UNIQUE constraint failed" in e.args[0]:
                    if "USER.username" in e.args[0]:
                        error = f"User {username} already exists."
                    if "USER.email" in e.args[0]:
                        error = f"Address {email} already exists."
            else:
                registration_mail(username, email, token)
                flash(f"A registration mail was sent to {email}")
                return redirect(url_for("auth.login"))
        flash(error)
    return render_template("auth/register.html")

@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM USER WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username"
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password"
        
        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            flash(f"You are now logged in {user["username"]}")
            return redirect(url_for("index"))

        flash(error)
    return render_template("auth/login.html")

@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@bp.route("/profile", methods=("GET", "POST"))
def profile():
    error = None
    user = g.user
    if user is None:
        error = "You must be logged in to see your profile"

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        is_notified = request.form.get("is_notified") == "on"

        if not username:
            error = "Username is required"
        if not email:
            error = "Email is required"
        
        if error is None:
            db = get_db()
            db.execute(
                """
                UPDATE USER
                SET username = ?,
                    email = ?,
                    is_notified = ?
                WHERE id = ?
                """, 
                (username, email, is_notified, user["id"],)
            )
            db.commit()
            
            flash(f"Your profile have been saved")
            return redirect(url_for("auth.profile"))

        if error:
            flash(error)

    if error:
        return redirect(url_for("index"))
    else:
        return render_template("auth/profile.html",
                                username=user["username"],
                                email=user["email"],
                                is_notified=user["is_notified"])

@bp.route("/verify/<token>", methods=("GET", "POST"))
def verify(token):
    db = get_db()
    error = None

    user = db.execute(
        "SELECT * FROM USER WHERE token = ? AND is_valid = FALSE", (token,)
    ).fetchone()

    if user is None:
        error = "Are you lost ?"

    if error is None:
        db.execute(
            """
            UPDATE USER
            SET is_valid = TRUE
            WHERE id = ?
            """, (user["id"],)
        )
        db.commit()

        session.clear()
        session["user_id"] = user["id"]
        flash(f"You are now verified. Welcome {user["username"]}")

    if error:
        flash(error)
    return redirect(url_for("index"))

@bp.route("/recovery", methods=("GET", "POST"))
def recovery():
    if request.method == "POST":
        email = request.form["email"]

        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE email = ?", (email,)
        ).fetchone()

        if user is None:
            error = "No user registered with this email"
        elif not user["is_valid"]:
            error = "No recovery for you, verify your email next time..."

        if error is None:
            token = secrets.token_urlsafe(16)
            db.execute(
                """
                UPDATE USER
                SET token = ?
                WHERE id = ?
                """, (token, user["id"],)
            )
            db.commit()

            recovery_mail(user["username"], email, token)
            flash(f"A password reset link was sent to {user["email"]}")
            return redirect(url_for("index"))

        flash(error)
    return render_template("auth/recovery.html")

@bp.route("/reset/<token>", methods=("GET", "POST"))
def reset(token):
    db = get_db()
    error = None

    user = db.execute(
        "SELECT * FROM user WHERE token = ?", (token,)
    ).fetchone()

    if user is None:
        error = "Are you lost ?"

    if error is None:
        db.execute(
            """
            UPDATE USER
            SET token = ''
            WHERE id = ?
            """, (user["id"],)
        )
        db.commit()

        session.clear()
        session["user_id"] = user["id"]
        return redirect(url_for("auth.password_reset"))

    flash(error)
    return redirect(url_for("index"))

@bp.route("/password_reset", methods=("GET", "POST"))
def password_reset():
    if request.method == "POST":
        password = request.form["password"]

        db = get_db()
        error = None
        user = g.user

        if user is None:
            error = "You must be logged in to change your password"

        if error is None:
            db.execute(
                """
                UPDATE USER
                SET password = ?
                WHERE id = ?
                """, (generate_password_hash(password), user["id"],)
            )
            db.commit()

            flash("Your password has been reset")
            return redirect(url_for("index"))

        flash(error)
    return render_template("auth/password_reset.html")