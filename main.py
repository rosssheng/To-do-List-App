from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_sqlalchemy import SQLAlchemy
import requests
import random
from flask_bootstrap import Bootstrap
from forms import LoginForm, RegisterForm, TodoForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from sqlalchemy.orm import relationship
from datetime import datetime
import os
from flask_migrate import Migrate

app = Flask(__name__)
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL1", "sqlite:///users.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "8BYkEfBA6O6donzWlSihBXox7C0sKR6b")
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Tables
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    todos = relationship("ToDo", back_populates="author")

class ToDo(db.Model):
    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    title = db.Column(db.String(250), unique=True, nullable=False)
    priority = db.Column(db.Boolean, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = relationship("User", back_populates="todos")


# Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))

        existing_username = User.query.filter_by(username=form.username.data).first()
        if existing_username:
            flash('Username already taken!', 'danger')
            return redirect(url_for('register'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            username=form.username.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("todo"))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field.capitalize()}: {error}', 'danger')

    return render_template("register.html", form=form, current_user=current_user)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('todo'))
    return render_template("login.html", form=form, current_user=current_user)

@app.route("/todo")
@login_required
def todo():
    todos = ToDo.query.filter_by(author=current_user).all()
    print(todos)
    return render_template("todo.html", all_todos=todos)

@app.route("/about")
@login_required
def about():
    return render_template("about.html", current_user=current_user)

@app.route("/logout")
def log_out():
    logout_user()
    return redirect(url_for('home'))



@app.route("/add_todo", methods=["GET", "POST"])
@login_required
def add_todo():
    form = TodoForm()
    if form.validate_on_submit():
        title = form.title.data
        priority = form.priority.data
        due_date = form.due_date.data
        body = form.body.data
        new_todo = ToDo(
            title=title,
            priority=priority,
            due_date=due_date,
            body=body,
            author=current_user)
        db.session.add(new_todo)
        db.session.commit()

        return redirect(url_for('todo'))
    return render_template("add_todo.html", form=form, current_user=current_user)



@app.route("/delete_todo/<int:todo_id>")
@login_required
def delete_todo(todo_id):
    todo_to_delete = ToDo.query.get(todo_id)
    if todo_to_delete and todo_to_delete.author_id == current_user.id:
        db.session.delete(todo_to_delete)
        db.session.commit()

    else:
        flash('TODO not found or you do not have permission to delete it!', 'danger')
    return redirect(url_for('todo'))

@app.route("/edit_todo/<int:todo_id>", methods=["GET", "POST"])
@login_required
def edit_todo(todo_id):
    todo_to_edit = ToDo.query.get(todo_id)
    date = todo_to_edit.due_date.date()

    edit_form = TodoForm(
        title= todo_to_edit.title,
        priority = todo_to_edit.priority,
        author = current_user,
        due_date = date,
        body = todo_to_edit.body

    )
    if edit_form.validate_on_submit():
        todo_to_edit.title = edit_form.title.data
        todo_to_edit.priority = edit_form.priority.data
        todo_to_edit.due_date = edit_form.due_date.data
        todo_to_edit.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for('show_todo', todo_id=todo_id))

    return render_template("add_todo.html", form = edit_form, is_edit=True, name=todo_to_edit.title, current_user=current_user,todo_id=todo_id)


@app.route("/todo/<int:todo_id>")
def show_todo(todo_id):
    todo = ToDo.query.get(todo_id)

    return render_template("comments.html", todo=todo, current_user=current_user)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)