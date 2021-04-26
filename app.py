import os

from datetime import datetime
from flask import Flask, render_template, flash, redirect, request, session, logging, url_for, Response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


from admin import UserModelView
from models import db, User, File, Advise

import flask_admin as admin
from flask_admin import expose
from flask_admin.base import AdminIndexView, BaseView
from flask_admin.menu import MenuLink

app = Flask(__name__, static_folder='')
app.config['SECRET_KEY'] = '!9m@S-dThyIlW[pHQbN^'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
db.create_all(app=app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login/', methods=['GET', 'POST'])
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
                if user.role == 'admin':
                    error = 'Invalid Credentials. Please try again.'
                    print(error)
                    return render_template('login.html', error=error)
                if user.role == 'doctor':
                    doctors = File.query.filter_by(assigned_to=str(user.id)).all()
                    return render_template('doctor.html', doctors=doctors)
                else:
                    patients = File.query.filter_by(uploaded_by=user.email).all()
                    return render_template('patient.html', patients=patients)
            else:
                error = 'Invalid Credentials. Please try again.'
                print(error)
                return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            error = "username alreadry exists."
            return render_template('register.html', error=error)
        hashed_password = generate_password_hash(request.form['password'], method='sha256')
        new_user = User(
            name=request.form['name'],
            email=request.form['email'],
            password=hashed_password,
            role='patient')
        db.session.add(new_user)
        db.session.commit()
        flash('You are successfully registered', 'success')
        return redirect(url_for('login'))
    else:
        return render_template('register.html')


@app.route('/submit/')
def submit():
    if session['logged_in']:
        doctors = User.query.filter_by(role='doctor').all()
        return render_template('patient_submit.html', doctors=doctors)
    return render_template('index.html')


@app.route('/file_upload/   ', methods=['GET', 'POST'])
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


@app.route('/add_advise/', methods=['GET', 'POST'])
def add_advise():
    msg = request.args['msg']
    print(msg)
    return redirect(url_for('login'))


@app.route('/logout/')
def logout():
    session['logged_in'] = False
    return redirect(url_for('index'))


@app.route('/admin_login', methods=['POST'])
def admin_login():
    if request.form['email'] == 'admin' and request.form['password'] == 'password':
        session['logged_in'] = True
        if 'user' in session:
            session.pop('user')
        return redirect('/user')
    super = User.query.filter_by(email=request.form['email']).first()
    if super:
        if check_password_hash(super.password, request.form['password']):
            if super.role == 'admin':
                session['logged_in'] = True
                return redirect('/user')
        if 'super' in session:
            session.pop('super')
            return redirect('/user')
        error = 'Invalid Credentials. Please try again.'
        return render_template('admin_login.html', error=error)
    error = 'Invalid Credentials. Please try again.'
    return render_template('admin_login.html', error=error)


@app.route('/admin_logout/')
def admin_logout():
    session['logged_in'] = False
    return render_template('admin_login.html')


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if session.get('logged_in'):
            if request.cookies.get('username'):
                return redirect('/user')
        if not session.get('logged_in'):
            return render_template('admin_login.html')
        return redirect('/user')


admin = admin.Admin(app, name='Admin', index_view=MyAdminIndexView(name=' '),
                    template_mode='bootstrap3',
                    url='/admin')
admin.add_view(UserModelView(User, db.session, url='/user'))
admin.add_link(MenuLink(name='Logout', category='', url="/admin_logout"))

if __name__ == '__main__':
    app.run(debug=True)
