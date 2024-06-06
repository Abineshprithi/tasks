from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Task
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        mobile_number = request.form['mobile_number']
        password = request.form['password']
        address = request.form['address']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        new_user = User(name=name, email=email, mobile_number=mobile_number, password=password, address=address, latitude=latitude, longitude=longitude)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    tasks = Task.query.filter_by(assigned_to=current_user.id).all()
    return render_template('dashboard.html', tasks=tasks)

@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    name = request.form['name']
    date_time = request.form['date_time']
    assigned_to = request.form['assigned_to']
    new_task = Task(name=name, date_time=datetime.strptime(date_time, '%Y-%m-%d %H:%M'), assigned_to=assigned_to)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    user = User.query.filter_by(email=email, password=password).first()
    if user:
        login_user(user)
        return jsonify({"message": "Login successful"})
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    name = data['name']
    email = data['email']
    mobile_number = data['mobile_number']
    password = data['password']
    address = data['address']
    latitude = data['latitude']
    longitude = data['longitude']
    new_user = User(name=name, email=email, mobile_number=mobile_number, password=password, address=address, latitude=latitude, longitude=longitude)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Registration successful"})

@app.route('/api/add_task', methods=['POST'])
@login_required
def api_add_task():
    data = request.get_json()
    name = data['name']
    date_time = data['date_time']
    assigned_to = data['assigned_to']
    new_task = Task(name=name, date_time=datetime.strptime(date_time, '%Y-%m-%d %H:%M'), assigned_to=assigned_to)
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task added successfully"})

@app.route('/api/tasks', methods=['GET'])
@login_required
def api_tasks():
    tasks = Task.query.filter_by(assigned_to=current_user.id).all()
    tasks_list = [{"name": task.name, "date_time": task.date_time, "status": task.status} for task in tasks]
    return jsonify(tasks_list)

if __name__ == '_main_':
    with app.app_context():
        db.create_all()
    app.run(debug=True)