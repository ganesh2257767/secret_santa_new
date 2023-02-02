from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
# from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from forms import RegistrationForm, LoginForm
from sqlalchemy.exc import IntegrityError


SECRET_KEY = os.urandom(32)

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)
app.app_context().push()

login_manager = LoginManager()
login_manager.init_app(app)



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    employee_id = db.Column(db.Integer, unique=True, index=True)
    email = db.Column(db.String(150), unique = True, index = True)
    joined_at = db.Column(db.DateTime(), default = datetime.utcnow, index = True)
    
    def __repr__(self):
        return f"{self.employee_id} - {self.email}"

    # def set_password(self, password):
    #     self.password_hash = generate_password_hash(password)

    # def check_password(self,password):
    #     return check_password_hash(self.password_hash,password)


@login_manager.user_loader
def load_user(user_id):
    print(user_id)
    print(User.query.get(user_id))
    return User.query.get(user_id)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', current_user=current_user)


@app.route('/', methods = ['POST','GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(first_name = form.first_name.data, last_name = form.last_name.data, employee_id=form.employee_id.data, email = form.email.data)
        # user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError as e:
            flash("User with this Email ID  or Employee ID is already registered.", category="danger")
            return redirect(url_for('register'))
            
        flash(f'{form.first_name.data.title()} {form.last_name.data.title()} registered successfully. Thank you.', category="success") 
        return redirect(url_for('register'))
    return render_template('registration.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None:
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid Email Address or Password.', 'danger')    
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)