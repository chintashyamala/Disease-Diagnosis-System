import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pickle
import numpy as np
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Needed for session management

# --- DATABASE CONFIGURATION ---
# Get the database URL from Render's environment, or use a local SQLite file as a fallback
db_url = os.environ.get('DATABASE_URL', 'sqlite:///local_test.db')
# Fix for SQLAlchemy 1.4+ which requires 'postgresql://' instead of 'postgres://'
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_key')

# --- LOGIN MANAGER CONFIGURATION ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Where to send users if they aren't logged in

# --- DATABASE MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    security_question = db.Column(db.String(200), nullable=False)
    security_answer = db.Column(db.String(200), nullable=False)
    
    records = db.relationship('PatientRecord', backref='author', lazy=True)

class PatientRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symptoms_input = db.Column(db.Text, nullable=False)
    predicted_disease = db.Column(db.String(100), nullable=False)
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow)
    # Foreign Key: Links this record to a specific user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# --- LOAD MODELS ---
model = pickle.load(open('models/disease_model.pkl', 'rb'))
symptoms_dict = pickle.load(open('models/symptoms_dict.pkl', 'rb'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES ---

@app.route('/')
def index():
    # If logged in, go to dashboard/predictor. If not, go to login.
    if current_user.is_authenticated:
        # Prepare symptom list for the predictor
        symptoms_list = [s.replace('_', ' ').title() for s in symptoms_dict.keys()]
        symptom_pairs = zip(symptoms_dict.keys(), symptoms_list)
        return render_template('index.html', symptoms=symptom_pairs, user=current_user)
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        question = request.form['security_question']
        answer = request.form['security_answer']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!')
            return redirect(url_for('register'))
        
        hashed_pw = generate_password_hash(password)
        # Save the question and hashed answer for security
        hashed_ans = generate_password_hash(answer.lower().strip()) 
        
        new_user = User(username=username, password_hash=hashed_pw, 
                        security_question=question, security_answer=hashed_ans)
        
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('index'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check your username and password.')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
@login_required  # Protect this route!
def predict():
    selected_symptoms = request.form.getlist('symptoms')
    
    # 1. ML Logic: Convert symptoms to 1s and 0s
    input_data = np.zeros(len(symptoms_dict))
    for symptom in selected_symptoms:
        if symptom in symptoms_dict:
            index = symptoms_dict[symptom]
            input_data[index] = 1
            
    # --- UNIQUE FEATURE: DIAGNOSTIC CONFIDENCE MATRIX ---
    # Get the probability score for EVERY disease
    probabilities = model.predict_proba([input_data])[0]
    
    # Get the names of all diseases the model knows
    disease_classes = model.classes_
    
    # Zip them together into a list of pairs: [('Fungal Infection', 0.85), ('Allergy', 0.12)...]
    disease_probs = list(zip(disease_classes, probabilities))
    
    # Sort the list from highest probability to lowest
    disease_probs.sort(key=lambda x: x[1], reverse=True)
    
    # Get the top 3 predictions, convert probability to a percentage (e.g., 85.0)
    # We only include them if the probability is greater than 0%
    top_3_predictions = [(disease, round(prob * 100, 2)) for disease, prob in disease_probs[:3] if prob > 0]
    
    # The #1 most likely prediction (for saving to the database)
    primary_prediction = top_3_predictions[0][0] if top_3_predictions else "Unknown"
    # ----------------------------------------------------
    
    # 2. Save to DB linked to CURRENT USER
    symptoms_str = ", ".join(selected_symptoms)
    new_record = PatientRecord(
        symptoms_input=symptoms_str, 
        predicted_disease=primary_prediction, # Save only the top result to history
        user_id=current_user.id  
    )
    
    db.session.add(new_record)
    db.session.commit()
    
    # 3. Pass the entire top_3 list to the HTML page
    return render_template('result.html', predictions=top_3_predictions)

@app.route('/history')
@login_required
def history():
    # Only fetch records for the CURRENT user
    user_records = PatientRecord.query.filter_by(user_id=current_user.id).order_by(PatientRecord.prediction_date.desc()).all()
    return render_template('history.html', records=user_records, user=current_user)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.form['username']
        answer = request.form['security_answer']
        new_password = request.form['new_password']
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            # Check if the security answer matches
            if check_password_hash(user.security_answer, answer.lower().strip()):
                # Reset the password
                user.password_hash = generate_password_hash(new_password)
                db.session.commit()
                flash('Password reset successful! Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Incorrect security answer.')
        else:
            flash('Username not found.')
            
    return render_template('reset_password.html')

@app.route('/delete/<int:record_id>', methods=['POST'])
@login_required
def delete_record(record_id):
    # Find the record or return a 404 error if it doesn't exist
    record = PatientRecord.query.get_or_404(record_id)
    
    # Security check: Ensure the current user owns this record
    if record.user_id == current_user.id:
        db.session.delete(record)
        db.session.commit()
        flash('Record deleted successfully.', 'success')
    else:
        flash('Unauthorized action.', 'error')
        
    # Refresh the history page
    return redirect(url_for('history'))

# Run once to create tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)