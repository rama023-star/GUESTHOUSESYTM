"""Dashboard views."""
import calendar
from datetime import date, timedelta
from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app.models import Property, Room
from app.utils import get_daily_summary, get_month_summary, get_heatmap_data, get_top_rooms, get_daily_series, local_today

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.get("/")
def home():
    return redirect(url_for("dashboard.index")) if current_user.is_authenticated else redirect(url_for("auth.login"))

@dashboard_bp.get("/dashboard")
@login_required
def index():
    today = local_today()
    year, month = request.args.get("year", today.year, type=int), request.args.get("month", today.month, type=int)
    if not 1 <= month <= 12 or year < 2000 or year > today.year + 1:
        abort(400)
    properties = Property.query.order_by(Property.id).all()
    selected = request.args.get("property", type=int)
    if current_user.role == "manager":
        selected = current_user.property_id
    elif selected not in [p.id for p in properties] and selected != 0:
        selected = 0
    scope = selected or None
    py, pm = (year - 1, 12) if month == 1 else (year, month - 1)
    ny, nm = (year + 1, 1) if month == 12 else (year, month + 1)
    room_count = Room.query.filter_by(active=True).filter(Room.property_id == scope).count() if scope else Room.query.filter_by(active=True).count()
    current_summary = get_month_summary(scope, year, month)
    previous_summary = get_month_summary(scope, py, pm)
    change = round((current_summary['revenue'] - previous_summary['revenue']) * 100 / previous_summary['revenue']) if previous_summary['revenue'] else None
    return render_template("dashboard.html", properties=properties, selected=selected, year=year, month=month, month_name=calendar.month_name[month], first_weekday=date(year, month, 1).weekday(),
        prev_y=py, prev_m=pm, next_y=ny, next_m=nm, today=get_daily_summary(scope, today),
        current=current_summary, previous=previous_summary,
        heatmap=get_heatmap_data(scope, year, month), top_rooms=get_top_rooms(scope, date(year, month, 1), date(ny, nm, 1)),
        rooms_total=room_count, today_date=today, chart_data=get_daily_series(scope, today - timedelta(days=29)),
        change_percent=change,
        no_data_today=(get_daily_summary(scope, today)['bookings'] == 0))
