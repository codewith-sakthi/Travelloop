import os
from datetime import datetime, timedelta, date
from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from sqlalchemy import or_
# pyrefly: ignore [missing-import]
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-for-traveloop'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///traveloop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.context_processor
def inject_globals():
    return dict(timedelta=timedelta, date=date)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    trips = db.relationship('Trip', backref='owner', lazy=True)

    def __init__(self, name: str, email: str, password: str) -> None:
        self.name = name
        self.email = email
        self.password = password

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    cover_photo = db.Column(db.String(255), nullable=True, default='default_trip.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=False)
    num_travelers = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    itinerary_items = db.relationship('ItineraryItem', backref='trip', lazy=True, cascade="all, delete-orphan")
    packing_items = db.relationship('PackingItem', backref='trip', lazy=True, cascade="all, delete-orphan")

    def __init__(self, name: str, start_date, end_date, user_id: int, description: str = '',
                 cover_photo: str = 'default_trip.jpg', is_public: bool = False, num_travelers: int = 1) -> None:
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.user_id = user_id
        self.description = description
        self.cover_photo = cover_photo
        self.is_public = is_public
        self.num_travelers = num_travelers

    @property
    def destination_count(self):
        return len(set(item.name for item in self.itinerary_items if item.category != 'hotel'))

class ItineraryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    day = db.Column(db.Integer, nullable=False, default=1)
    time = db.Column(db.String(50), nullable=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    cost = db.Column(db.Float, default=0.0)

    def __init__(self, trip_id, day, name, category, time=None, description=None, cost=0.0):
        self.trip_id = trip_id
        self.day = day
        self.name = name
        self.category = category
        self.time = time
        self.description = description
        self.cost = cost

class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False) # 'hotel', 'food', 'activity'
    country = db.Column(db.String(100), nullable=True)
    cost_index = db.Column(db.String(10), nullable=True) # e.g. '$', '$$', '$$$'
    popularity = db.Column(db.Float, nullable=True) # e.g. 4.8
    image_url = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    price_per_unit = db.Column(db.Float, nullable=True)

    def __init__(self, name: str, category: str, country: str = '', cost_index: str = '$', popularity: float = 0.0, image_url: str = '', description: str = '', price_per_unit: float = 0.0) -> None:
        self.name = name
        self.category = category
        self.country = country
        self.cost_index = cost_index
        self.popularity = popularity
        self.image_url = image_url
        self.description = description
        self.price_per_unit = price_per_unit

class PackingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    item = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), default='General')
    is_packed = db.Column(db.Boolean, default=False)

    def __init__(self, trip_id, item, category='General', is_packed=False):
        self.trip_id = trip_id
        self.item = item
        self.category = category
        self.is_packed = is_packed

class CommunityPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationships
    user = db.relationship('User', backref='posts', lazy=True)
    trip = db.relationship('Trip', backref='community_posts', lazy=True)
    likes = db.relationship('PostLike', backref='post', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('PostComment', backref='post', lazy=True, cascade='all, delete-orphan', order_by='PostComment.created_at')

class PostLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('community_post.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='_user_post_like_uc'),)

class PostComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('community_post.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='comments', lazy=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('signup'))
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('dashboard'))
        
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check email and password.')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    recent_trips = Trip.query.filter_by(user_id=current_user.id).order_by(Trip.created_at.desc()).limit(3).all()
    for trip in recent_trips:
        trip.total_cost = sum(item.cost or 0 for item in trip.itinerary_items)
        
    top_destinations = Place.query.order_by(Place.popularity.desc()).limit(4).all()
    return render_template('dashboard.html', trips=recent_trips, top_destinations=top_destinations)

@app.route('/trips/create', methods=['GET', 'POST'])
@login_required
def create_trip():
    if request.method == 'POST':
        name = request.form.get('name')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        description = request.form.get('description', '')
        num_travelers = int(request.form.get('num_travelers', 1) or 1)

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format')
            return redirect(url_for('create_trip'))

        new_trip = Trip(name=name, start_date=start_date, end_date=end_date,
                        description=description, user_id=current_user.id,
                        num_travelers=num_travelers)
        db.session.add(new_trip)
        db.session.commit()
        return redirect(url_for('my_trips'))
        
    return render_template('create_trip.html')

@app.route('/trips')
@login_required
def my_trips():
    trips = Trip.query.filter_by(user_id=current_user.id).order_by(Trip.start_date.desc()).all()
    # Calculate costs for display in template
    for trip in trips:
        trip.total_cost = sum(item.cost or 0 for item in trip.itinerary_items)
    return render_template('my_trips.html', trips=trips)

@app.route('/trips/<int:trip_id>')
@login_required
def view_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id and not trip.is_public:
        flash("You do not have access to this trip.")
        return redirect(url_for('dashboard'))
    
    # Group items by day
    days = {}
    for item in trip.itinerary_items:
        if item.day not in days:
            days[item.day] = []
        days[item.day].append(item)
    
    # Sort days
    sorted_days = sorted(days.keys())
    
    # Calculate totals
    total_spent = sum(item.cost or 0 for item in trip.itinerary_items)
    category_totals = {}
    for item in trip.itinerary_items:
        cat = item.category.lower() if item.category else 'activity'
        if 'hotel' in cat: display_cat = 'Accommodation'
        elif 'food' in cat: display_cat = 'Food'
        else: display_cat = 'Activities'
        cost = item.cost or 0
        category_totals[display_cat] = category_totals.get(display_cat, 0) + cost
        
    return render_template('itinerary_view.html', 
                           trip=trip, 
                           days=days, 
                           sorted_days=sorted_days,
                           total_spent=total_spent,
                           category_totals=category_totals)

@app.route('/api/trips/<int:trip_id>/save_itinerary', methods=['POST'])
@login_required
def save_itinerary(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    items = data.get('items', [])
    
    # Clear existing items
    ItineraryItem.query.filter_by(trip_id=trip_id).delete()
    
    for item in items:
        name = item.get('name')
        if not name: continue  # Skip invalid items
        
        try:
            cost = float(item.get('cost', 0) or 0)
        except (TypeError, ValueError):
            cost = 0.0
            
        new_item = ItineraryItem(
            trip_id=trip_id,
            day=item.get('day', 1),
            time=item.get('time'),
            name=name,
            category=item.get('category') or 'activity',
            description=item.get('description'),
            cost=cost
        )
        db.session.add(new_item)
    
    db.session.commit()
    return jsonify({"status": "success"})
@app.route('/ai-planner')
@login_required
def ai_planner():
    return render_template('ai_planner.html')

@app.route('/community')
@login_required
def community_feed():
    posts = CommunityPost.query.order_by(CommunityPost.created_at.desc()).all()
    # Check if user has liked each post
    liked_post_ids = [like.post_id for like in PostLike.query.filter_by(user_id=current_user.id).all()]
    return render_template('community_feed.html', posts=posts, liked_post_ids=liked_post_ids)

@app.route('/community/share', methods=['POST'])
@login_required
def share_trip():
    trip_id = request.form.get('trip_id')
    title = request.form.get('title')
    description = request.form.get('description', '')
    
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    post = CommunityPost(
        user_id=current_user.id,
        trip_id=trip_id,
        title=title,
        description=description
    )
    db.session.add(post)
    db.session.commit()
    flash('Trip shared with the community!')
    return redirect(url_for('community_feed'))

@app.route('/community/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    like = PostLike.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if like:
        db.session.delete(like)
        liked = False
    else:
        new_like = PostLike(user_id=current_user.id, post_id=post_id)
        db.session.add(new_like)
        liked = True
    db.session.commit()
    return jsonify({"status": "success", "liked": liked, "count": PostLike.query.filter_by(post_id=post_id).count()})

@app.route('/community/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    body = request.form.get('body')
    if not body:
        return redirect(url_for('view_post', post_id=post_id))
    
    comment = PostComment(
        user_id=current_user.id,
        post_id=post_id,
        body=body
    )
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('view_post', post_id=post_id))

@app.route('/community/post/<int:post_id>')
@login_required
def view_post(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    is_liked = PostLike.query.filter_by(user_id=current_user.id, post_id=post_id).first() is not None
    return render_template('post_detail.html', post=post, is_liked=is_liked)

@app.route('/api/trips/<int:trip_id>/copy', methods=['POST'])
@login_required
def copy_trip(trip_id):
    original = Trip.query.get_or_404(trip_id)
    
    # Create new trip
    new_trip = Trip(
        user_id=current_user.id,
        name=f"Copy of {original.name}",
        start_date=original.start_date,
        end_date=original.end_date,
        description=original.description,
        num_travelers=original.num_travelers,
        cover_photo=original.cover_photo
    )
    db.session.add(new_trip)
    db.session.flush() # Get new_trip.id
    
    # Copy itinerary items
    for item in original.itinerary_items:
        new_item = ItineraryItem(
            trip_id=new_trip.id,
            day=item.day,
            name=item.name,
            category=item.category,
            time=item.time,
            description=item.description,
            cost=item.cost
        )
        db.session.add(new_item)
        
    # Copy packing items
    for p_item in original.packing_items:
        new_p = PackingItem(
            trip_id=new_trip.id,
            item=p_item.item,
            category=p_item.category,
            is_packed=False
        )
        db.session.add(new_p)
        
    db.session.commit()
    return jsonify({"status": "success", "new_trip_id": new_trip.id})

@app.route('/trips/<int:trip_id>/packing')
@login_required
def packing_list(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    
    # Group items by category
    categories = {}
    for item in trip.packing_items:
        cat = item.category or 'General'
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)
        
    return render_template('packing_list.html', trip=trip, categories=categories)

@app.route('/api/trips/<int:trip_id>/packing/add', methods=['POST'])
@login_required
def add_packing_item(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    new_item = PackingItem(
        trip_id=trip_id,
        item=data.get('item'),
        category=data.get('category', 'General')
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"status": "success", "id": new_item.id})

@app.route('/api/packing/<int:item_id>/toggle', methods=['POST'])
@login_required
def toggle_packing_item(item_id):
    item = PackingItem.query.get_or_404(item_id)
    trip = Trip.query.get(item.trip_id)
    if trip.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    item.is_packed = not item.is_packed
    db.session.commit()
    return jsonify({"status": "success", "is_packed": item.is_packed})

@app.route('/api/packing/<int:item_id>', methods=['DELETE'])
@login_required
def delete_packing_item(item_id):
    item = PackingItem.query.get_or_404(item_id)
    trip = Trip.query.get(item.trip_id)
    if trip.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    db.session.delete(item)
    db.session.commit()
    return jsonify({"status": "success"})
@app.route('/trips/<int:trip_id>/build')
@login_required
def build_itinerary(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    
    num_days = (trip.end_date - trip.start_date).days + 1
    return render_template('itinerary_builder.html', trip=trip, num_days=num_days)

@app.route('/trips/<int:trip_id>/delete', methods=['POST'])
@login_required
def delete_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id == current_user.id:
        db.session.delete(trip)
        db.session.commit()
        flash('Trip deleted successfully.')
    return redirect(url_for('my_trips'))

# API route for places suggestions — prioritises Indian places
@app.route('/api/search_places')
def search_places():
    query = request.args.get('q', '').strip().lower()
    category = request.args.get('category', 'all').lower()
    limit = int(request.args.get('limit', 12))

    places_query = Place.query
    if category != 'all':
        places_query = places_query.filter_by(category=category)

    if query:
        # Aggressively clean query: remove common travel-related words
        clean_query = query.lower()
        # Remove common phrases
        for s in ['trip to ', 'visit to ', 'my trip to ', 'tour of ', 'exploring ', ' trip', ' tour', ' vacation', ' visit']:
            clean_query = clean_query.replace(s, '')
            
        clean_query = clean_query.strip()
        
        places_query = places_query.filter(
            or_(
                Place.name.ilike(f'%{clean_query}%'),
                Place.country.ilike(f'%{clean_query}%'),
                Place.description.ilike(f'%{clean_query}%')
            )
        )

    # Sort by popularity descending — highest-rated Indian places first
    places = places_query.order_by(Place.popularity.desc()).limit(limit).all()

    results = []
    for p in places:
        results.append({
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "country": p.country,
            "cost_index": p.cost_index,
            "popularity": p.popularity,
            "image_url": p.image_url,
            "price": p.price_per_unit,
            "description": p.description
        })
    return jsonify(results)

# Top curated Indian suggestions for the create-trip page cards
@app.route('/api/top_suggestions')
@login_required
def top_suggestions():
    top = Place.query.filter(
        Place.popularity >= 4.7
    ).order_by(Place.popularity.desc()).limit(6).all()
    return jsonify([{
        'id': p.id, 'name': p.name, 'country': p.country,
        'category': p.category, 'popularity': p.popularity,
        'price': p.price_per_unit, 'image_url': p.image_url,
        'description': p.description
    } for p in top])

import random

# Advanced AI Feature: Smart Itinerary Generator
@app.route('/api/ai_generate_itinerary', methods=['POST'])
@login_required
def ai_generate_itinerary():
    data = request.json
    trip_id = data.get('trip_id')
    vibe = data.get('vibe', 'balanced') # 'relaxing', 'adventure', 'cultural'
    
    trip = Trip.query.get(trip_id)
    if not trip or trip.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    # AI Logic: Filter top places matching the vibe
    places_query = Place.query.filter(Place.popularity >= 4.2)
    if vibe == 'cultural':
        places_query = places_query.filter(Place.category == 'activity')
    elif vibe == 'relaxing':
        places_query = places_query.filter(Place.category.in_(['hotel', 'food']))
        
    available_places = places_query.limit(50).all()
    
    # Generate a smart day plan
    selected = random.sample(available_places, min(4, len(available_places)))
    
    ai_schedule = []
    times = ["09:00 AM", "01:00 PM", "04:00 PM", "07:30 PM"]
    
    for i, p in enumerate(selected):
        ai_schedule.append({
            "time": times[i % len(times)],
            "name": p.name,
            "category": p.category,
            "cost": p.price_per_unit,
            "ai_insight": f"✨ AI Suggests: Perfectly matches your {vibe} vibe with a {p.popularity} rating."
        })
        
    return jsonify({
        "status": "success",
        "message": f"AI generated a {vibe} itinerary!",
        "schedule": ai_schedule
    })

def init_db():
    with app.app_context():
        db.create_all()
        # Seed the suggestions if empty
        if Place.query.count() == 0:
            sample_places = [
                # pyre-ignore[28]
                Place(name="Grand Plaza Hotel", category="hotel", country="USA", cost_index="$$$", popularity=4.8, price_per_unit=150.0, image_url="https://images.unsplash.com/photo-1566073771259-6a8506099945?w=200", description="Luxury stay with great views."),
                # pyre-ignore[28]
                Place(name="National Museum", category="activity", country="USA", cost_index="$", popularity=4.9, price_per_unit=25.0, image_url="https://images.unsplash.com/photo-1518998053401-a4149019651c?w=200", description="Explore historical artifacts."),
                # pyre-ignore[28]
                Place(name="Bistro Downtown", category="food", country="USA", cost_index="$$", popularity=4.6, price_per_unit=40.0, image_url="https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=200", description="A cozy place for fine dining."),
            ]
            db.session.bulk_save_objects(sample_places)
            db.session.commit()
            print("Database initialized and seeded with sample places.")
        else:
            print("Database initialized.")

@app.route('/api/ai_smart_plan', methods=['POST'])
@login_required
def ai_smart_plan():
    data = request.json
    destination = data.get('destination', '').strip()
    trip_days = int(data.get('trip_days', 1))
    travel_type = data.get('travel_type', 'solo')
    interests = data.get('interests', [])
    budget = data.get('budget', 'medium')
    
    # 1. Analyze destination and find nearby places
    search_pattern = f"%{destination}%"
    nearby = Place.query.filter(
        or_(
            Place.name.ilike(search_pattern),
            Place.country.ilike(search_pattern),
            Place.description.ilike(search_pattern)
        )
    ).order_by(Place.popularity.desc()).all()
    
    if not nearby:
        nearby = Place.query.order_by(Place.popularity.desc()).limit(20).all()
        
    filtered_places = []
    for p in nearby:
        match_score = 0
        desc = (p.description or '').lower()
        cat = (p.category or '').lower()
        for interest in interests:
            if interest.lower() in desc or interest.lower() in cat:
                match_score += 1
        p.match_score = match_score
        filtered_places.append(p)
    
    filtered_places.sort(key=lambda x: (x.match_score, x.popularity or 0), reverse=True)
    
    places_json = []
    for i, p in enumerate(filtered_places[:15]):
        dist = 5 + (i * 3)
        priority = "Must Visit" if i < 5 else "Recommended" if i < 10 else "Optional"
        
        places_json.append({
            "place_name": p.name,
            "distance": f"{dist} km",
            "priority": priority,
            "category": p.category or "Sightseeing",
            "why_visit": (p.description[:150] + "...") if p.description else "A top-rated local attraction.",
            "best_time_to_visit": "October to March",
            "estimated_duration": "2-3 hours",
            "travel_time_from_destination": f"{dist * 2} mins"
        })
        
    flow = {}
    for d in range(1, trip_days + 1):
        day_key = f"day_{d}"
        day_places = filtered_places[(d-1)*3 : d*3]
        if not day_places and filtered_places:
            day_places = filtered_places[:3]
            
        flow[day_key] = {
            "morning": [day_places[0].name] if len(day_places) > 0 else ["Local Exploration"],
            "afternoon": [day_places[1].name] if len(day_places) > 1 else ["Lunch & Sightseeing"],
            "evening": [day_places[2].name] if len(day_places) > 2 else ["Relaxing Walk"]
        }
        
    response = {
        "destination": destination,
        "trip_summary": {
            "days": trip_days,
            "travel_type": travel_type,
            "budget": budget,
            "theme": ", ".join(interests) if interests else "General"
        },
        "nearby_places": places_json,
        "smart_itinerary_flow": flow,
        "food_recommendations": [
            "Local Street Food Stall (Try regional specialties)",
            "High-rated Heritage Restaurant",
            "Popular Cafe with a View"
        ],
        "hidden_gems": [p.name for p in filtered_places[10:13]] if len(filtered_places) > 12 else ["Local Artisan Market"]
    }
    
    return jsonify(response)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=7000)
