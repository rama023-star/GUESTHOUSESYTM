"""Booking entry."""
from datetime import date
from flask import Blueprint, flash, redirect, render_template, request, url_for, abort
from flask_login import current_user, login_required
from app import db
from app.models import Booking, Property, Room, AuditLog
from app.utils import local_today
input_bp = Blueprint("input", __name__)

@input_bp.route("/input", methods=["GET", "POST"])
@login_required
def index():
    try:
        day = date.fromisoformat(request.values.get("date", local_today().isoformat()))
    except ValueError:
        day = local_today()
    if day > local_today():
        day = local_today()
    props = Property.query.order_by(Property.id).all()
    prop_id = current_user.property_id if current_user.role == "manager" else request.values.get("property", type=int)
    if not prop_id and props:
        prop_id = props[0].id
    if request.method == "POST":
        try:
            action = request.form.get("action", "add")
            room = db.session.get(Room, int(request.form["room_id"]))
            count = int(request.form.get("count", 1))
            if day > local_today() or not room or room.property_id != prop_id or (action == "add" and (not room.active or count < 1 or count > 100)):
                raise ValueError
            if action == "add":
                for _ in range(count):
                    booking = Booking(room_id=room.id, date=day, amount=room.price, recorded_by=current_user.id)
                    db.session.add(booking)
                    db.session.flush()
                    db.session.add(AuditLog(user_id=current_user.id, action="create", entity="booking", entity_id=booking.id, new_value=str(room.price)))
            elif action == "remove":
                booking = Booking.query.filter_by(room_id=room.id, date=day).order_by(Booking.created_at.desc(), Booking.id.desc()).first()
                if not booking or (current_user.role != "admin" and day != local_today()):
                    raise ValueError
                db.session.add(AuditLog(user_id=current_user.id, action="delete", entity="booking", entity_id=booking.id, old_value=str(booking.amount)))
                db.session.delete(booking)
            else:
                raise ValueError
            db.session.commit()
            flash((f"Recorded {count} booking(s) for {room.name}." if action == "add" else f"Removed the latest booking for {room.name}."), "success")
        except (ValueError, KeyError):
            db.session.rollback()
            flash("Choose a valid room and booking count.", "error")
        return redirect(url_for("input.index", date=day.isoformat(), property=prop_id))
    rooms = Room.query.filter_by(active=True, property_id=prop_id).order_by(Room.name).all() if prop_id else []
    totals = {r.id: (0, 0) for r in rooms}
    if rooms:
        aggregates = db.session.query(Booking.room_id, db.func.count(Booking.id), db.func.coalesce(db.func.sum(Booking.amount), 0)).filter(
            Booking.room_id.in_([room.id for room in rooms]), Booking.date == day
        ).group_by(Booking.room_id).all()
        totals.update({room_id: (int(count), int(revenue)) for room_id, count, revenue in aggregates})
    undo = Booking.query.filter_by(recorded_by=current_user.id).order_by(Booking.created_at.desc(), Booking.id.desc()).first()
    booking_rows = Booking.query.join(Room).filter(Booking.date == day, Room.property_id == prop_id).order_by(Booking.created_at.desc()).all() if current_user.role == "admin" else []
    all_count = sum(x[0] for x in totals.values()); all_revenue = sum(int(x[1]) for x in totals.values())
    return render_template("input.html", rooms=rooms, totals=totals, properties=props, property_id=prop_id, day=day, today=local_today(), undo=undo,
                           total_bookings=all_count, total_revenue=all_revenue, can_edit=(current_user.role == "admin" or day == local_today()), booking_rows=booking_rows)


@input_bp.post("/input/undo")
@login_required
def undo():
    booking = Booking.query.filter_by(recorded_by=current_user.id).order_by(Booking.created_at.desc(), Booking.id.desc()).first()
    if booking and (current_user.role == "admin" or booking.date == local_today()):
        db.session.add(AuditLog(user_id=current_user.id, action="delete", entity="booking", entity_id=booking.id, old_value=str(booking.amount)))
        room_id = booking.room_id; prop_id = booking.room.property_id; day = booking.date
        db.session.delete(booking); db.session.commit(); flash("Last booking undone.", "success")
        return redirect(url_for("input.index", property=prop_id, date=day.isoformat()))
    flash("There is no recent booking you can undo.", "error")
    return redirect(url_for("input.index"))


@input_bp.post("/input/bookings/<int:booking_id>/edit")
@login_required
def edit_booking(booking_id):
    if current_user.role != "admin":
        abort(403)
    booking = db.session.get(Booking, booking_id)
    if not booking: abort(404)
    try:
        new_day = date.fromisoformat(request.form.get("date", ""))
        new_amount = int(request.form.get("amount", "0"))
        if new_day > local_today() or new_amount < 1: raise ValueError
        old_value = f"date={booking.date.isoformat()},amount={booking.amount}"
        booking.date, booking.amount = new_day, new_amount
        db.session.add(AuditLog(user_id=current_user.id, action="update", entity="booking", entity_id=booking.id,
                                old_value=old_value, new_value=f"date={new_day.isoformat()},amount={new_amount}"))
        db.session.commit(); flash("Booking updated.", "success")
    except (ValueError, TypeError):
        db.session.rollback(); flash("Choose a valid date and positive whole-number amount.", "error")
    return redirect(url_for("input.index", property=booking.room.property_id, date=booking.date.isoformat()))


@input_bp.post("/input/bookings/<int:booking_id>/delete")
@login_required
def delete_booking(booking_id):
    if current_user.role != "admin": abort(403)
    booking = db.session.get(Booking, booking_id)
    if not booking: abort(404)
    prop_id, day = booking.room.property_id, booking.date
    db.session.add(AuditLog(user_id=current_user.id, action="delete", entity="booking", entity_id=booking.id, old_value=str(booking.amount)))
    db.session.delete(booking); db.session.commit()
    flash("Booking deleted.", "success")
    return redirect(url_for("input.index", property=prop_id, date=day.isoformat()))
