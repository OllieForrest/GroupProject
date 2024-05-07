from app import db
from app.models import Post
from sqlalchemy.orm import sessionmaker

def delete_all_posts():
    try:
        # Create a new database session
        Session = sessionmaker(bind=db.engine)
        session = Session()

        # Delete all records from the Post table
        session.query(Post).delete()

        # Commit the changes to persist the deletion
        session.commit()
        print("All posts have been deleted successfully.")

    except Exception as e:
        # Rollback the session if an error occurs
        session.rollback()
        print(f"Error deleting posts: {e}")

    finally:
        # Close the session
        session.close()

# Call the delete_all_posts function
if __name__ == "__main__":
    delete_all_posts()
