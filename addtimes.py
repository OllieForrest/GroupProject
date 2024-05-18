import random
from datetime import datetime, timedelta
from app import app, db
from app.models import Post

def random_date_within_last_month():
    today = datetime(2024, 5, 18)  # assuming today is 18 May 2024
    start_date = today - timedelta(days=30)
    random_seconds = random.randint(0, int((today - start_date).total_seconds()))
    return start_date + timedelta(seconds=random_seconds)

with app.app_context():
    all_posts = Post.query.all()
    for post in all_posts:
        post.created_at = random_date_within_last_month()
        db.session.add(post)
    db.session.commit()
    print(f"Updated {len(all_posts)} posts with random creation dates.")
