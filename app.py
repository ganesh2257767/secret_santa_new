from flask import Flask, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import check_password_hash
from datetime import datetime
from forms import RegistrationForm, LoginForm
from sqlalchemy.exc import IntegrityError, PendingRollbackError
import os, random, base64, io, math
from PIL import Image

MYSQLDATABASE = os.getenv("MYSQLDATABASE")
MYSQLHOST = os.getenv("MYSQLHOST")
MYSQLPASSWORD = os.getenv("MYSQLPASSWORD")
MYSQLPORT = os.getenv("MYSQLPORT")
MYSQLUSER = os.getenv("MYSQLUSER")

SECRET_KEY = os.urandom(32)

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{MYSQLUSER}:{MYSQLPASSWORD}@{MYSQLHOST}:{MYSQLPORT}/{MYSQLDATABASE}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)
app.app_context().push()

login_manager = LoginManager()
login_manager.init_app(app)


def process_image(raw_data):
    buffer = io.BytesIO() # Create a Bytes IO buffer
    raw_data = Image.open(raw_data)
    raw_data.save(buffer, format="JPEG", optimize=True, quality=10)

    downloadable_data = buffer.getvalue()
    
    resized_image = raw_data.resize((100, 100), Image.Resampling.LANCZOS)
    resized_image.save(buffer, format="JPEG", optimize=True, quality=20)
    renderable_data = buffer.getvalue()
    renderable_data = base64.b64encode(renderable_data).decode('ascii')
    
    return downloadable_data, renderable_data


def get_user_details():
    return User.query.with_entities(User.first_name, User.last_name, User.email).all()


def send_emails(form):
    form = form.to_dict(flat=False)
    mappings = list(zip(form['to'], form['from']))


    for mapping in mappings:
        user = User.query.filter_by(email=mapping[0]).first()
        print(f"""\n\nYou will send your gift to {user.first_name} {user.last_name}.
              Find their contact details below:
              Name: {user.first_name} {user.last_name}.
              Address: {user.address}.
              Mobile Number: {user.mobile_number}.
              Email ID: {user.email}

              (Send this email to {mapping[1]})""")


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    employee_id = db.Column(db.BigInteger, unique=True, index=True)
    email = db.Column(db.String(150), unique = True, index = True)
    address = db.Column(db.Text, nullable=False)
    mobile_number = db.Column(db.BigInteger, unique=True, nullable=False)
    joined_at = db.Column(db.DateTime(), default = datetime.utcnow, index = True)
    gift = db.relationship('Gift', backref='user', uselist=False, cascade="all, delete")
    
    def __repr__(self):
        return f"{self.employee_id} - {self.email}"


class Gift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gift_image_download = db.Column(db.LargeBinary(length=(2**32)-1), nullable=False)
    gift_image_render = db.Column(db.Text(length=(2**32)-1), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f"""Gift from: {self.user_id.email_id}"""


class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique = True, index = True)
    password = db.Column(db.String(150), index = True)


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(user_id)


@app.route('/dashboard')
@login_required
def dashboard():
    users = get_user_details()
    return render_template('dashboard.html', total=len(users), users=users)


@app.route('/', methods = ['POST','GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        
        downloadable_image, renderable_image = process_image(form.gift_image.data)
        
        user = User(first_name = form.first_name.data.title(),
                    last_name = form.last_name.data.title(),
                    employee_id = form.employee_id.data,
                    email = form.email.data,
                    address = form.address.data.title(),
                    mobile_number = form.mobile_number.data)
        gift = Gift(gift_image_download = downloadable_image,
                    gift_image_render = renderable_image,
                    user = user)

        db.session.add(user)
        db.session.add(gift)
        try:
            db.session.commit()
        except IntegrityError as e:
            flash("User with this Email ID  or Employee ID is already registered.", category="danger")
            return redirect(url_for('register'))
        except PendingRollbackError:
            db.session.rollback()
            
        flash(f'{form.first_name.data.title()} {form.last_name.data.title()} registered successfully. Thank you.', category="success") 
        return redirect(url_for('register'))
    total = len(get_user_details())
    return render_template('registration.html', form=form, total=total)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            admin = Admin.query.filter_by(email = form.email.data).first()
        except PendingRollbackError:
            db.session.rollback()
        else:
            if admin is not None and check_password_hash(admin.password, form.password.data):
                login_user(admin)
                return redirect(url_for('dashboard'))
            flash('Invalid Email Address or Password.', 'danger')    
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))


@app.route('/play', methods=['GET', 'POST'])
@login_required
def play():
    if request.method == 'GET':
        participants = User.query.all()
        gifts = Gift.query.all()
        random.shuffle(gifts)
        random.shuffle(participants)
        return render_template('play.html', participants=participants, gifts=gifts)
    else:
        send_emails(request.form)
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)