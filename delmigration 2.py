from sqlalchemy import create_engine, MetaData

# Replace the following line with your actual database URI
engine = create_engine('sqlite:///app.db')  # Adjust this to your actual connection string
meta = MetaData()
meta.bind = engine  # Bind the engine to MetaData like this

# Your other operations can go here
# For example, to drop all tables safely:
meta.reflect(bind=engine)
meta.drop_all(bind=engine)
