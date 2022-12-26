from flask import Flask, render_template, abort, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, AddForm, DeletionForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

owners = [1]
login_manager = LoginManager()
login_manager.init_app(app)

# Connect to Database
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

logged_in = False
current_user_id = 0

# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)
    def to_dictionary(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)

# db.create_all()

def admin_only(function):
    @wraps(function)
    def wrapper_function(*args, **kwargs):
        if current_user_id == 1:
            return function(*args, **kwargs)
        else:
            return abort(403, "You are not authorized to view this page, sucker hahaha.")
    return wrapper_function

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/")
def home():
    all_cafes = Cafe.query.all()
    # posts = all_cafes
    return render_template("index.html", all_cafes=all_cafes,
                           logged_in=logged_in, current_user_id=current_user_id,
                           owners=owners)

@app.route('/register', methods=["POST", "GET"])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        new_user = User()
        new_user.email = request.form["email"]
        new_user.name = request.form["name"]
        user_in_db = User.query.filter_by(email=new_user.email).first()
        if user_in_db:
            error = "You already have signed up with that email, log in instead."
            login_form = LoginForm()
            return render_template("login.html", form=login_form, error=error)
        new_user.password = generate_password_hash(
            password=request.form["password"],
            method="pbkdf2:sha256",
            salt_length=8
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        global logged_in, current_user_id
        logged_in = True
        current_user_id = new_user.id
        return redirect(url_for("home", logged_in=logged_in))
    return render_template("register.html", form=register_form)

@app.route('/login', methods=["POST", "GET"])
def login():
    login_form = LoginForm()
    error = None
    if login_form.validate_on_submit():
        email_entered = request.form["email"]
        password_entered = request.form["password"]
        user_in_db = User.query.filter_by(email=email_entered).first()
        if user_in_db:
            password_in_db = user_in_db.password
            if check_password_hash(pwhash=password_in_db, password=password_entered):
                login_user(user_in_db)
                global logged_in, current_user_id
                logged_in = True
                current_user_id = user_in_db.id
                return redirect(url_for("home"))
            else:
                error = "Invalid Password"
        else:
            error = "No user with that email exists."
    return render_template("login.html", form=login_form, error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    global logged_in, current_user_id
    logged_in = False
    current_user_id = 0
    return redirect(url_for('home'))

@app.route('/add_cafe', methods=["GET", "POST"])
@login_required
def add_cafe():
    add_form = AddForm()
    if add_form.validate_on_submit():
        new_cafe = Cafe(
            name=add_form.name.data,
            location=add_form.location.data,
            map_url=add_form.map_url.data,
            img_url=add_form.img_url.data,
            seats=add_form.seats.data,
            coffee_price=add_form.coffee_price.data,
            has_toilet=True if add_form.has_toilet.data.lower() == "yes" else False,
            has_wifi=True if add_form.has_wifi.data.lower() == "yes" else False,
            has_sockets=True if add_form.has_sockets.data.lower() == "yes" else False,
            can_take_calls=True if add_form.can_take_calls.data.lower() == "yes" else False
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_cafe.html", form=add_form, logged_in=logged_in)

@app.route("/delete/<int:post_id>", methods=["POST", "GET"])
@admin_only
def delete_post(post_id):
    post_to_delete = Cafe.query.get(post_id)
    form = DeletionForm()
    if form.validate_on_submit():
        if form.cancel.data:
            return redirect(url_for("home"))
        elif form.delete.data:
            db.session.delete(post_to_delete)
            db.session.commit()
            return redirect(url_for('home'))
    return render_template("deletion_confirmation.html", form=form, post_to_delete=post_to_delete)

@app.route("/edit-post/<int:post_id>", methods=["POST", "GET"])
@admin_only
def edit_post(post_id):
    cafe = Cafe.query.get(post_id)
    edit_form = AddForm(
        name=cafe.name,
        location=cafe.location,
        img_url=cafe.img_url,
        map_url=cafe.map_url,
        seats=cafe.seats,
        coffee_price=cafe.coffee_price,
        has_toilet="Yes" if cafe.has_toilet else "No",
        has_wifi="Yes" if cafe.has_wifi else "No",
        has_sockets="Yes" if cafe.has_sockets else "No",
        can_take_calls="Yes" if cafe.can_take_calls else "No"
    )
    if edit_form.validate_on_submit():
        cafe.name = edit_form.name.data
        cafe.location = edit_form.location.data
        cafe.map_url = edit_form.map_url.data
        cafe.img_url = edit_form.img_url.data
        cafe.seats = edit_form.seats.data
        cafe.coffee_price = edit_form.coffee_price.data
        cafe.has_toilet = True if edit_form.has_toilet.data.lower() == "yes" else False
        cafe.has_wifi = True if edit_form.has_wifi.data.lower() == "yes" else False
        cafe.has_sockets = True if edit_form.has_sockets.data.lower() == "yes" else False
        cafe.can_take_calls = True if edit_form.can_take_calls.data.lower() == "yes" else False
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_cafe.html", form=edit_form, logged_in=logged_in)

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

if __name__ == '__main__':
    app.run(debug=True)
