import pytest
from app import create_app, db
from app.models import Property, Room, User


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    CURRENCY_CODE = "UGX"
    TIMEZONE = "Africa/Kampala"


@pytest.fixture()
def app():
    application = create_app(TestConfig)
    with application.app_context():
        db.create_all()
        lodge = Property(name="Lodge A")
        other = Property(name="Lodge B")
        db.session.add_all([lodge, other]); db.session.flush()
        admin = User(name="Admin", email="admin@example.test", role="admin")
        admin.set_password("admin-password")
        manager = User(name="Manager", email="manager@example.test", role="manager", property_id=lodge.id)
        manager.set_password("manager-password")
        outsider = User(name="Other", email="other@example.test", role="manager", property_id=other.id)
        outsider.set_password("other-password")
        db.session.add_all([admin, manager, outsider, Room(property_id=lodge.id, name="Room 1", price=40000), Room(property_id=other.id, name="Room 2", price=80000)])
        db.session.commit()
        yield application
        db.session.remove(); db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client, email, password):
    return client.post("/login", data={"email": email, "password": password}, follow_redirects=True)
