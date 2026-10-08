"""Authentication views and role guards."""
from functools import wraps
from flask import Blueprint, flash, redirect, render_template, request, url_for, abort
from urllib.parse import urlparse
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User

auth_bp = Blueprint("auth", __name__)


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user.role != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def manager_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user.role not in ("admin", "manager"):
            abort(403)
        return view(*args, **kwargs)
    return wrapped


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        user = User.query.filter_by(email=request.form.get("email", "").strip().lower(), active=True).first()
        if user and user.check_password(request.form.get("password", "")):
            login_user(user)
            target = request.args.get("next", "")
            if target and urlparse(target).netloc == "" and target.startswith("/") and not target.startswith("//"):
                return redirect(target)
            return redirect(url_for("dashboard.index"))
        flash("Email or password is incorrect.", "error")
    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

