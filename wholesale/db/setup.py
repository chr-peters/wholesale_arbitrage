from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from wholesale.settings import DATABASE_MYSQL

connection_url = (
    f"mysql+pymysql://{DATABASE_MYSQL['USER']}:"
    f"{DATABASE_MYSQL['PASSWORD']}@{DATABASE_MYSQL['HOST']}/"
    f"{DATABASE_MYSQL['DBNAME']}"
)

engine = create_engine(connection_url)
Session = sessionmaker(bind=engine)
