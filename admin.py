from flask import session, flash
from werkzeug.security import generate_password_hash
from flask_admin.contrib.sqla import ModelView
from wtforms import PasswordField

from wtforms.validators import required, DataRequired

from models import db


class MyModeView(ModelView):
    def is_accessible(self):
        if session.get('logged_out'):
            return False
        if session.get('logged_in'):
            return True


class UserModelView(MyModeView):
    column_list = ['name', 'email', 'role']
    form_columns = ['name', 'email', 'password', 'role']

    def on_form_prefill(self, form, id):
        form.password.data = ''

    form_args = {
        'email': {
            'validators': [required()]
        },
        'password': {
            'default': '',
            'validators': [DataRequired(), ]
        },

    }
    form_extra_fields = {
        'password': PasswordField('Password')
    }
    form_choices = {
        'role': [
            ('admin', 'admin'),
            ('doctor', 'doctor'),
        ]
    }

    def create_model(self, form):
        if form.data['password'] == '':
            flash("Password Required", "error")
            return False
        model = super().create_model(form)
        model.password = generate_password_hash(form.data['password'], method='sha256')
        db.session.add(model)
        db.session.commit()
        return model

    def update_model(self, form, model):
        if form.data['password'] == '':
            flash("Password Required", "error")
            return False
        updated = super().update_model(form, model)
        if updated:
            model.password = generate_password_hash(form.data['password'], method='sha256')
            db.session.commit()
        return updated
