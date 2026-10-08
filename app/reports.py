"""Booking reports and CSV export."""
import csv, io
from datetime import date, timedelta
from flask import Blueprint, Response, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy import func
from app import db
from app.models import Booking, Property, Room
from app.utils import local_today
reports_bp = Blueprint("reports", __name__)

@reports_bp.get("/reports")
@login_required
def index():
    today = local_today()
    try:
        start = date.fromisoformat(request.args.get("start", (today-timedelta(days=29)).isoformat()))
        end = date.fromisoformat(request.args.get("end", today.isoformat()))
    except ValueError:
        start, end = today-timedelta(days=29), today
    props = Property.query.order_by(Property.id).all()
    prop_id = current_user.property_id if current_user.role == "manager" else request.args.get("property", type=int)
    if end < start or (end - start).days > 3660:
        flash("Choose a valid date range no longer than 10 years.", "error")
        start, end = today-timedelta(days=29), today
    query = db.session.query(Room.name, func.count(func.distinct(Booking.date)), func.count(Booking.id), func.coalesce(func.sum(Booking.amount), 0)).join(Booking).filter(Booking.date >= start, Booking.date <= end)
    if prop_id:
        query = query.filter(Room.property_id == prop_id)
    rows = query.group_by(Room.id).order_by(Room.name).all()
    totals = (sum(r[1] for r in rows), sum(r[2] for r in rows), sum(int(r[3]) for r in rows))
    if request.args.get("format") == "csv":
        stream = io.StringIO(); writer = csv.writer(stream)
        writer.writerow(["Room", "Days worked", "Bookings", "Revenue"]); writer.writerows(rows); writer.writerow(["TOTAL", *totals])
        return Response(stream.getvalue(), mimetype="text/csv", headers={"Content-Disposition":"attachment; filename=guestflow-report.csv"})
    return render_template("reports.html", rows=rows, start=start, end=end, properties=props, property_id=prop_id, totals=totals)
