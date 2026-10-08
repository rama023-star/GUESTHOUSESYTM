"""Admin room and staff management."""
from flask import Blueprint, flash, redirect, render_template, request, url_for, abort
from sqlalchemy.exc import IntegrityError
from app import db
from app.auth import admin_required
from app.models import Property, Room, User
manage_bp = Blueprint("manage", __name__, url_prefix="/manage")

@manage_bp.get("")
@admin_required
def index():
    return render_template("manage/index.html", properties=Property.query.order_by(Property.id).all(), rooms=Room.query.order_by(Room.property_id, Room.name).all(), managers=User.query.filter_by(role="manager").order_by(User.name).all())

@manage_bp.post("/rooms")
@admin_required
def add_room():
    try:
        prop = db.session.get(Property, int(request.form["property_id"]))
        name, price = request.form["name"].strip(), int(request.form["price"])
        if not prop or not name or price < 1: raise ValueError
        db.session.add(Room(property_id=prop.id, name=name, price=price)); db.session.commit(); flash("Room added.", "success")
    except (KeyError, ValueError):
        db.session.rollback(); flash("Enter a valid room name, property, and price.", "error")
    return redirect(url_for("manage.index"))

@manage_bp.post("/rooms/<int:room_id>/deactivate")
@admin_required
def deactivate_room(room_id):
    room = db.session.get(Room, room_id)
    if room is None: abort(404)
    room.active = False; db.session.commit(); flash("Room deactivated.", "success")
    return redirect(url_for("manage.index"))


@manage_bp.post("/rooms/<int:room_id>/edit")
@admin_required
def edit_room(room_id):
    room = db.session.get(Room, room_id)
    if not room: abort(404)
    try:
        name, price = request.form.get("name", "").strip(), int(request.form.get("price", "0"))
        prop = db.session.get(Property, int(request.form.get("property_id", "0")))
        if not name or price < 1 or not prop: raise ValueError
        room.name, room.price, room.property_id = name, price, prop.id
        db.session.commit(); flash("Room updated.", "success")
    except (ValueError, TypeError):
        db.session.rollback(); flash("Enter a valid room name, property, and whole-number price.", "error")
    return redirect(url_for("manage.index"))


@manage_bp.post("/rooms/<int:room_id>/restore")
@admin_required
def restore_room(room_id):
    room = db.session.get(Room, room_id)
    if not room: abort(404)
    room.active = True; db.session.commit(); flash("Room reactivated.", "success")
    return redirect(url_for("manage.index"))


@manage_bp.post("/managers")
@admin_required
def add_manager():
    try:
        name, email = request.form.get("name", "").strip(), request.form.get("email", "").strip().lower()
        password, prop = request.form.get("password", ""), db.session.get(Property, int(request.form.get("property_id", "0")))
        if not name or "@" not in email or len(password) < 8 or not prop: raise ValueError
        user = User(name=name, email=email, role="manager", property_id=prop.id); user.set_password(password)
        db.session.add(user); db.session.commit(); flash("Manager added.", "success")
    except IntegrityError:
        db.session.rollback(); flash("That email address is already in use.", "error")
    except (ValueError, TypeError):
        db.session.rollback(); flash("Enter a name, valid email, password (8+ characters), and property.", "error")
    return redirect(url_for("manage.index", tab="managers"))


@manage_bp.post("/managers/<int:user_id>/edit")
@admin_required
def edit_manager(user_id):
    user = db.session.get(User, user_id)
    if not user or user.role != "manager": abort(404)
    try:
        name, email = request.form.get("name", "").strip(), request.form.get("email", "").strip().lower()
        prop = db.session.get(Property, int(request.form.get("property_id", "0")))
        if not name or "@" not in email or not prop: raise ValueError
        user.name, user.email, user.property_id = name, email, prop.id
        user.active = request.form.get("active") == "1"
        if request.form.get("password"):
            if len(request.form["password"]) < 8: raise ValueError
            user.set_password(request.form["password"])
        db.session.commit(); flash("Manager updated.", "success")
    except IntegrityError:
        db.session.rollback(); flash("That email address is already in use.", "error")
    except (ValueError, TypeError):
        db.session.rollback(); flash("Enter valid manager details and a password of at least 8 characters.", "error")
    return redirect(url_for("manage.index", tab="managers"))


@manage_bp.post("/properties/<int:property_id>/edit")
@admin_required
def edit_property(property_id):
    prop = db.session.get(Property, property_id)
    if not prop: abort(404)
    name = request.form.get("name", "").strip()
    if not name:
        flash("Property name is required.", "error")
    else:
        prop.name = name
        try: db.session.commit(); flash("Property renamed.", "success")
        except IntegrityError: db.session.rollback(); flash("That property name is already in use.", "error")
    return redirect(url_for("manage.index", tab="properties"))
