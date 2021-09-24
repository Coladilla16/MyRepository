from flask import Blueprint
#from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for, request, flash, redirect, render_template
import flask_login

from flask_wtf import FlaskForm
# from wtforms import StringField, PasswordField
# from wtforms.validators import DataRequired, Email, EqualTo

from . import login_manager, bcrypt, db
from . import model

bp = Blueprint('auth', __name__, template_folder='templates')


# # Authentication forms
# class LoginForm(FlaskForm):
#     email = StringField('Email', validators=[DataRequired(), Email()])
#     password = PasswordField('Password', validators=[DataRequired()])


# class RegistrationForm(FlaskForm):
#     email = StringField('Email', validators=[DataRequired(), Email()])
#     first_name = StringField('First Name', validators=[DataRequired()])
#     last_name = StringField('Last Name', validators=[DataRequired()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])



@bp.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for('main.home'))



@bp.route("/login")
def login():
    return render_template("auth/login.html")


@bp.route("/login", methods=["POST"])
def login_post():
    # Complete the following two lines:
    email = request.form.get("email")
    password = request.form.get("password")
    # Get the user with that email from the database:
    user = model.User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        # The user exists and the password is correct
        flask_login.login_user(user)
        return redirect(url_for("main.home"))
        #return redirect(url_for("auth.signup"))
    else:
        # Wrong email and/or password
        # Complete this code to flash a message and redirect to the login form
        flash("Sorry, Wrong email and/or password")
        return redirect(url_for("auth/login.html"))
    
    return redirect(url_for("main.home"))







@bp.route("/signup")
def signup():
    return render_template("auth/signup.html")


@bp.route("/signup", methods=["POST"])
def signup_post():
    email = request.form.get("email")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")

    password = request.form.get("password")
    # Check that passwords are equal
    if password != request.form.get("password_repeat"):
        flash("Sorry, passwords are different")
        return redirect(url_for("auth.signup"))
    # Check if the email is already at the database
    user = model.User.query.filter_by(email=email).first()
    if user:
        flash("Sorry, the email you provided is already registered")
        return redirect(url_for("auth.signup"))
    

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = model.User(email=email, first_name = first_name, last_name = last_name, password=password_hash)
    db.session.add(new_user)
    db.session.commit()
    flash("You've successfully signed up!")
    return render_template('auth/signup.html')




@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth/login'))


@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return model.User.query.get(user_id)
    return None