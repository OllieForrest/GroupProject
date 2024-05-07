from app import db
from app.models import Post
def delete_all_posts():
    try:
        # Delete all posts from the database
        db.session.query(Post).delete()
        db.session.commit()
        print("All posts have been deleted successfully.")
    except Exception as e:
        db.session.rollback()
        print("Error occurred while deleting posts:", e)

if __name__ == "__main__":
    delete_all_posts()
