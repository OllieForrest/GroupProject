from urllib.parse import urlsplit
from flask import abort, render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForms, RegistrationForm
from app.models import User, Guess
from flask import render_template
from datetime import datetime, timezone
from flask import request
import urllib.request
from flask import redirect, url_for
from werkzeug.utils import secure_filename
from app.models import Post
import base64
import random
from sqlalchemy import or_

@app.route('/postingpage')
def postpage():
    return render_template('createpost.html', title="Create User Post")


@app.route('/')
def landingpage():
    return render_template('landingpage.html', title='ValueCheck')


@app.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 2
    guessed_posts_ids = [guess.post_id for guess in Guess.query.filter_by(user_id=current_user.id).all()]
    posts = Post.query.filter(Post.id.notin_(guessed_posts_ids)).paginate(page=page, per_page=per_page)
    query = request.args.get('query', None)


    if query:
        posts = Post.query.filter(
            or_(
                Post.description.ilike(f'%{query}%'), 
                Post.item_name.ilike(f'%{query}%')
            )
        ).paginate(page=page, per_page=10)
    else:
        posts = Post.query.paginate(page=page, per_page=10)

    return render_template('index.html', posts=posts, query=query)


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
    return redirect(url_for('landingpage'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, points = 0)
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

@app.route('/createposts', methods=['POST'])
@login_required
def posting():
    if request.method == 'POST':
        item_name = request.form['itemName']
        description = request.form['description']
        category = request.form['category']
        condition = request.form['condition']
        starting_price = float(request.form['startingPrice'])
        sold_price = float(request.form['soldPrice'])
        user_id = current_user.id  
        pic= request.files['picture']
        upper_limit = int(3.5 * (int(sold_price)))
        maxslider = random.randint(int(sold_price) , upper_limit)


        if not pic:
            return "No pic uploaded", 400
        
        filename= secure_filename(pic.filename)
        mimetype = pic.mimetype
        img = pic.read()  
        
        img_base64 = base64.b64encode(img).decode("utf-8")
        
        new_post = Post(
            item_name=item_name,
            description=description,
            category=category,
            condition=condition,
            starting_price=starting_price,
            user_id=user_id,
            picture_name=filename,
            img=img_base64,  
            mimetype=mimetype,
            author=current_user,
            sold_price= sold_price,
            maxslider = maxslider
        )
        db.session.add(new_post)
        db.session.commit()
        flash('Congratulations, you have posted!')
        return redirect(url_for('index')) 

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get(post_id)
    if post:
        db.session.delete(post)
        db.session.commit()
    else:
        flash('Post not found.', 'error')
    return redirect(url_for('index'))

@app.route('/search')
def search():
    query = request.args.get('query', '')
    if query:
        search_results = Post.query.filter(
            or_(
                Post.description.ilike(f'%{query}%'), 
                Post.item_name.ilike(f'%{query}%')
            )
        ).all()
        return render_template('results.html', posts=search_results)
    else:
        return redirect(url_for('index'))


@app.route('/submit_guess/<int:post_id>', methods=['POST'])
def submit_guess(post_id):
    existing_guess = Guess.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if existing_guess:
        flash('You have already made a guess for this post.')
        return redirect(url_for('index'))

    post = Post.query.get_or_404(post_id)
    guessed_price = float(request.form['guess_price'])

    new_guess = Guess(user_id=current_user.id, post_id=post_id, guessed_price=guessed_price)
    db.session.add(new_guess)
    
    error = abs(post.sold_price - guessed_price)
    points_awarded = max(0, 100 - int(error / 100)) 
    current_user.points += points_awarded

    db.session.commit()
    return redirect(url_for('index'))

@app.route('/contact_us')
def contact_us():
    return render_template('contactus.html', title="Contact Us")
