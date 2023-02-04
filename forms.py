from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, DataRequired, Email, Regexp

class RegistrationForm(FlaskForm):
    employee_id = StringField('Employee ID', validators=[InputRequired(), DataRequired(), Regexp(regex='^[0-9]+$', message="Use numbers only.")])
    first_name = StringField('First Name', validators = [InputRequired(), DataRequired()])
    last_name = StringField('Last Name', validators = [InputRequired(), DataRequired()])
    email = StringField('Email', validators= [InputRequired(), DataRequired(), Email(), Regexp(regex="^[a-zA-Z]+.?[a-zA-Z]+[0-9]?@?(amdocs)\\.com$", message="Email should be of the format Name.Surname@Amdocs.com")])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[InputRequired(), DataRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')