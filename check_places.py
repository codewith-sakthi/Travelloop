from app import app, db, Place
with app.app_context():
    places = Place.query.all()
    for p in places:
        print(f"ID: {p.id} | Name: {p.name} | Image: {p.image_url}")
