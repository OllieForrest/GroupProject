from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForms, RegistrationForm
from app.models import User
from flask import render_template
from datetime import datetime, timezone
from flask import request, jsonify
import json
from flask import redirect, url_for

@app.route('/createposts')
def posting():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Save the filename to the database for the post
        # Example: post.photo_filename = filename
        return 'File uploaded successfully'
    return render_template('createpost.html', title="Create Your Posts!")

@app.route('/')
def landingpage():
    return render_template('landingpage.html', title='ValueCheck')

@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', posts=posts,)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForms()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/my_account/<username>')
@login_required
def my_account(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    return render_template('account.html', title='My Account', user=user)

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard_1.html', title='Leaderboard')


@app.route('/update_user', methods=['GET','POST'])
@login_required
def edit_profile():
    username = request.form.get('username')
    about_me = request.form.get('about_me')
    email = request.form.get('email')

    current_user.username = username
    current_user.about_me = about_me
    current_user.email = email
    db.session.commit()
    
    return redirect(url_for('my_account', username=current_user.username))


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

