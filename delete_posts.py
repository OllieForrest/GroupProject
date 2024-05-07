from app import app, db
from app.models import Post

def delete_all_posts():
    with app.app_context():
        try:
            db.session.query(Post).delete()
            db.session.commit()
            print("All posts deleted successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting posts: {e}")

if __name__ == "__main__":
    delete_all_posts()
