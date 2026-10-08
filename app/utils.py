"""Reusable booking aggregations."""
import calendar
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from flask import current_app
from sqlalchemy import func
from app import db
from app.models import Booking, Room


def local_today() -> date:
    """Return the current calendar date in the configured property timezone."""
    return datetime.now(ZoneInfo(current_app.config.get("TIMEZONE", "Africa/Kampala"))).date()


def _scope(query, property_id):
    if property_id is not None:
        query = query.join(Room, Booking.room_id == Room.id).filter(Room.property_id == property_id)
    return query


def get_daily_summary(property_id: int | None, day: date):
    """Return booking count and revenue for a property on one calendar day."""
    q = _scope(db.session.query(func.count(Booking.id), func.coalesce(func.sum(Booking.amount), 0)), property_id)
    count, revenue = q.filter(Booking.date == day).one()
    worked = _scope(db.session.query(func.count(func.distinct(Booking.room_id))), property_id).filter(Booking.date == day).scalar() or 0
    return {"bookings": count, "revenue": int(revenue), "rooms_worked": worked}


def get_month_summary(property_id: int | None, year: int, month: int):
    """Return booking totals for a month."""
    start = date(year, month, 1)
    end = date(year + (month == 12), month % 12 + 1, 1)
    q = _scope(db.session.query(func.count(Booking.id), func.coalesce(func.sum(Booking.amount), 0)), property_id)
    count, revenue = q.filter(Booking.date >= start, Booking.date < end).one()
    return {"bookings": count, "revenue": int(revenue)}


def get_heatmap_data(property_id: int | None, year: int, month: int):
    """Return one revenue cell for every day of the requested month."""
    days = calendar.monthrange(year, month)[1]
    start = date(year, month, 1)
    end = start + timedelta(days=days)
    q = _scope(db.session.query(Booking.date, func.count(Booking.id), func.coalesce(func.sum(Booking.amount), 0)), property_id)
    rows = q.filter(Booking.date >= start, Booking.date < end).group_by(Booking.date).all()
    daily = {d: (int(n), int(v)) for d, n, v in rows}
    max_revenue = max((v for _, v in daily.values()), default=0)
    result = []
    for offset in range(days):
        day = start + timedelta(days=offset)
        count, revenue = daily.get(day, (0, 0))
        level = 0 if revenue == 0 or max_revenue == 0 else min(4, (revenue * 4 + max_revenue - 1) // max_revenue)
        result.append({"date": day.isoformat(), "revenue": revenue, "bookings": count, "level": level})
    return result


def get_top_rooms(property_id: int | None, start: date, end: date, limit: int = 5):
    """Return rooms ordered by revenue during [start, end)."""
    q = db.session.query(Room.id, Room.name, func.coalesce(func.sum(Booking.amount), 0).label("revenue"))
    q = q.join(Booking, Booking.room_id == Room.id).filter(Room.active.is_(True), Booking.date >= start, Booking.date < end)
    if property_id is not None:
        q = q.filter(Room.property_id == property_id)
    return [{"room_id": rid, "name": name, "revenue": int(revenue)} for rid, name, revenue in q.group_by(Room.id).order_by(func.sum(Booking.amount).desc()).limit(limit).all()]


def get_daily_series(property_id: int | None, start: date, days: int = 30) -> list[dict]:
    """Return revenue and booking counts for consecutive days, including empty days."""
    end = start + timedelta(days=days)
    query = _scope(db.session.query(Booking.date, func.count(Booking.id), func.coalesce(func.sum(Booking.amount), 0)), property_id)
    rows = query.filter(Booking.date >= start, Booking.date < end).group_by(Booking.date).all()
    grouped = {day: (int(count), int(revenue)) for day, count, revenue in rows}
    return [{"date": (start + timedelta(days=i)).isoformat(), "bookings": grouped.get(start + timedelta(days=i), (0, 0))[0], "revenue": grouped.get(start + timedelta(days=i), (0, 0))[1]} for i in range(days)]

