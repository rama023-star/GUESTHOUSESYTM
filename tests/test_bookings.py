from datetime import date
from app import db
from app.models import Booking, AuditLog
from conftest import login


def test_manager_can_create_booking_for_own_property(app, client):
    login(client, "manager@example.test", "manager-password")
    response = client.post("/input", data={"room_id": 1, "count": 2, "date": date.today().isoformat(), "property": 1}, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        bookings = Booking.query.filter_by(room_id=1, date=date.today()).all()
        assert len(bookings) == 2
        assert {b.amount for b in bookings} == {40000}


def test_manager_cannot_book_another_property(app, client):
    login(client, "manager@example.test", "manager-password")
    client.post("/input", data={"room_id": 2, "count": 1, "date": date.today().isoformat(), "property": 1}, follow_redirects=True)
    with app.app_context():
        assert Booking.query.count() == 0


def test_booking_is_audited_and_can_be_removed(app, client):
    login(client, "manager@example.test", "manager-password")
    client.post("/input", data={"room_id": 1, "count": 1, "date": date.today().isoformat(), "property": 1})
    client.post("/input", data={"room_id": 1, "action": "remove", "date": date.today().isoformat(), "property": 1})
    with app.app_context():
        assert Booking.query.count() == 0
        assert AuditLog.query.count() == 2
