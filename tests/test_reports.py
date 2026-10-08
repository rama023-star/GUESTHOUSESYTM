from datetime import date
from app import db
from app.models import Booking
from app.utils import get_daily_summary, get_month_summary, get_heatmap_data
from conftest import login


def test_summary_aggregations(app):
    with app.app_context():
        db.session.add_all([Booking(room_id=1, date=date.today(), amount=40000, recorded_by=1), Booking(room_id=1, date=date.today(), amount=50000, recorded_by=1)])
        db.session.commit()
        daily = get_daily_summary(1, date.today())
        monthly = get_month_summary(1, date.today().year, date.today().month)
        assert daily == {"bookings": 2, "revenue": 90000, "rooms_worked": 1}
        assert monthly == {"bookings": 2, "revenue": 90000}
        assert len(get_heatmap_data(1, date.today().year, date.today().month)) in range(28, 32)


def test_reports_has_totals_and_csv(client):
    login(client, "admin@example.test", "admin-password")
    html = client.get("/reports").data
    assert b"Grand total" in html
    csv = client.get("/reports?format=csv").data
    assert b"Room,Days worked,Bookings,Revenue" in csv


def test_manager_reports_are_property_scoped(client):
    login(client, "manager@example.test", "manager-password")
    assert client.get("/reports?property=2").status_code == 200
