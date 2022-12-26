from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


# WTForm
class AddForm(FlaskForm):
    name = StringField("Cafe Name", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    map_url = StringField("Google Map URL", validators=[DataRequired(), URL()])
    img_url = StringField("Cafe Image URL", validators=[DataRequired(), URL()])
    seats = StringField("Number of Seats", validators=[DataRequired()])
    has_toilet = StringField("Does the Cafe Have a Toilet? Enter Yes or No", validators=[DataRequired()])
    has_wifi = StringField("Does the Cafe Have WiFi? Enter Yes or No", validators=[DataRequired()])
    has_sockets = StringField("Does the Cafe Have Power Sockets? Enter Yes or No", validators=[DataRequired()])
    can_take_calls = StringField("Can You Comfortably Make Audio/Video Calls? Enter Yes or No",
                                 validators=[DataRequired()])
    coffee_price = StringField("Coffee Price in Dollars, Just Enter the Number",
                                 validators=[DataRequired()])
    submit = SubmitField("Submit")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    name = StringField("Your Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


# class CommentForm(FlaskForm):
#     comment = CKEditorField("Comment", validators=[DataRequired()])
#     submit = SubmitField("Submit Comment")


class DeletionForm(FlaskForm):
    cancel = SubmitField("Cancel")
    delete = SubmitField("Delete")
