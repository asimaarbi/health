import os
from datetime import datetime
from flask import Flask, render_template, flash, redirect, request, session, logging, url_for
from models import db, User, File, Advise
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = '!9m@S-dThyIlW[pHQbN^'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
db.create_all(app=app)


@app.route('/')
def index():
    print(os.getcwd())
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            if check_password_hash(user.password, request.form['password']):
                flash('You have successfully logged in.', "success")
                session['logged_in'] = True
                session['name'] = user.name
                session['email'] = user.email
                session['uid'] = user.id
                if user.role == 'doctor':
                    doctors = File.query.filter_by(assigned_to=str(user.id)).all()
                    return render_template('doctor.html', doctors=doctors)
                else:
                    patients = File.query.filter_by(uploaded_by=user.email).all()
                    return render_template('patient.html', patients=patients)
            else:
                flash('Username or Password Incorrect', "Danger")
                return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            flash("username alreadry exists")
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(request.form['password'], method='sha256')
        new_user = User(
            name=request.form['name'],
            email=request.form['email'],
            password=hashed_password,
            role=request.form['role'])
        db.session.add(new_user)
        db.session.commit()
        flash('You are successfully registered', 'success')
        return redirect(url_for('login'))
    else:
        return render_template('register.html')


@app.route('/submit')
def submit():
    if session['logged_in']:
        doctors = User.query.filter_by(role='doctor').all()
        return render_template('patient_submit.html', doctors=doctors)
    return render_template('index.html')


@app.route('/file_upload', methods=['GET', 'POST'])
def file_upload():
    if request.method == 'POST':
        pic = request.files['file']

        if pic.filename:
            filename = secure_filename(str(datetime.now()) + pic.filename)
            pic.save(os.path.abspath(os.path.join("static/", os.path.join('images', filename))))
        else:
            filename = ""
        new_file = File(
            assigned_to=request.form['doctor'],
            file=filename,
            uploaded_by=request.form['user'])
        db.session.add(new_file)
        db.session.commit()
    patients = File.query.filter_by(uploaded_by=request.form['user']).all()
    return render_template('patient.html', patients=patients)


@app.route('/logout/')
def logout():
    session['logged_in'] = False
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
