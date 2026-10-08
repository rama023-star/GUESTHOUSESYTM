from datetime import date, timedelta
import random
from app import create_app, db
from app.models import Property, User, Room, Booking
from app.utils import local_today
app = create_app()
with app.app_context():
    db.create_all()
    if not Property.query.first():
        a,b=Property(name="Lodge A"),Property(name="Lodge B")
        db.session.add_all([a,b]); db.session.flush()
        admin=User(name="GuestFlow Admin",email="admin@guestflow.local",role="admin"); admin.set_password("changeme123"); db.session.add(admin)
        for prop,count in ((a,10),(b,8)):
            manager=User(name=f"{prop.name} Manager",email=f"manager-{prop.name[-1].lower()}@guestflow.local",role="manager",property_id=prop.id); manager.set_password("changeme123"); db.session.add(manager)
            rooms=[]
            for n in range(1,count+1):
                room=Room(property_id=prop.id,name=f"Room {n:02d}",price=random.randrange(4,9)*10000); db.session.add(room); rooms.append(room)
            db.session.flush()
            for days in range(60,0,-1):
                workday=local_today()-timedelta(days=days)
                for room in rooms:
                    for _ in range(random.choices([0,1,2],[.40,.48,.12])[0]): db.session.add(Booking(room_id=room.id,date=workday,amount=room.price,recorded_by=manager.id))
        db.session.commit(); print("Seeded GuestFlow. Admin: admin@guestflow.local / changeme123")
    else: print("Database already contains data; seed skipped.")
