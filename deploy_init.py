"""Prepare the database and first admin account during a production deploy."""
import os

from app import create_app, db
from app.models import Property, User


app = create_app()


def initialize() -> None:
    """Create initial tables/properties and an admin from deployment secrets."""
    with app.app_context():
        db.create_all()
        if Property.query.count() == 0:
            db.session.add_all([Property(name="Lodge A"), Property(name="Lodge B")])

        if not User.query.filter_by(role="admin").first():
            email = os.environ.get("BOOTSTRAP_ADMIN_EMAIL", "").strip().lower()
            password = os.environ.get("BOOTSTRAP_ADMIN_PASSWORD", "")
            name = os.environ.get("BOOTSTRAP_ADMIN_NAME", "GuestFlow Admin").strip()
            if not email or "@" not in email or len(password) < 12 or not name:
                raise RuntimeError("Set BOOTSTRAP_ADMIN_EMAIL and a 12+ character BOOTSTRAP_ADMIN_PASSWORD before deploying.")
            admin = User(name=name, email=email, role="admin")
            admin.set_password(password)
            db.session.add(admin)
        db.session.commit()


if __name__ == "__main__":
    initialize()
