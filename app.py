import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
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

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    cover_photo = db.Column(db.String(255), nullable=True, default='default_trip.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def destination_count(self):
        # mock implementation for now
        return 0

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
    return render_template('dashboard.html', trips=recent_trips)

@app.route('/trips/create', methods=['GET', 'POST'])
@login_required
def create_trip():
    if request.method == 'POST':
        name = request.form.get('name')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        description = request.form.get('description')
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format')
            return redirect(url_for('create_trip'))
            
        new_trip = Trip(name=name, start_date=start_date, end_date=end_date, 
                       description=description, user_id=current_user.id)
        db.session.add(new_trip)
        db.session.commit()
        return redirect(url_for('my_trips'))
        
    return render_template('create_trip.html')

@app.route('/trips')
@login_required
def my_trips():
    trips = Trip.query.filter_by(user_id=current_user.id).order_by(Trip.start_date.desc()).all()
    return render_template('my_trips.html', trips=trips)

@app.route('/trips/<int:trip_id>')
@login_required
def view_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id and not trip.is_public:
        flash("You do not have access to this trip.")
        return redirect(url_for('dashboard'))
    return render_template('itinerary_view.html', trip=trip)

@app.route('/trips/<int:trip_id>/build')
@login_required
def build_itinerary(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    return render_template('itinerary_builder.html', trip=trip)

@app.route('/trips/<int:trip_id>/delete', methods=['POST'])
@login_required
def delete_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id == current_user.id:
        db.session.delete(trip)
        db.session.commit()
        flash('Trip deleted successfully.')
    return redirect(url_for('my_trips'))

# Mock API routes for interactive elements
@app.route('/api/search_cities')
def search_cities():
    query = request.args.get('q', '').lower()
    # Mock data
    cities = [
        {"id": 1, "name": "Paris", "country": "France", "cost_index": "$$$", "popularity": 9.5},
        {"id": 2, "name": "Tokyo", "country": "Japan", "cost_index": "$$$", "popularity": 9.8},
        {"id": 3, "name": "Rome", "country": "Italy", "cost_index": "$$", "popularity": 9.2},
        {"id": 4, "name": "Bali", "country": "Indonesia", "cost_index": "$", "popularity": 8.9}
    ]
    if query:
        cities = [c for c in cities if query in c['name'].lower() or query in c['country'].lower()]
    return jsonify(cities)

def init_db():
    with app.app_context():
        db.create_all()
        print("Database initialized.")

if __name__ == '__main__':
    if not os.path.exists('traveloop.db'):
        init_db()
    app.run(debug=True, port=5000)
