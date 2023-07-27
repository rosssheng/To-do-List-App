from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, DateField
from wtforms.validators import DataRequired, Email, ValidationError



# TODO 3: Create form for TO-DO List



class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_confirm_password(self, field):
        if self.password.data != field.data:
            raise ValidationError('Passwords must match.')


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class TodoForm(FlaskForm):
    title = StringField("Task Name", validators=[DataRequired()])
    priority = BooleanField("Priority")
    due_date = DateField("Due Date", validators=[DataRequired()])
    body = StringField("Task Comments", validators=[DataRequired()])
    submit = SubmitField("Submit")
