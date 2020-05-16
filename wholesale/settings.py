import os

DATABASE_MYSQL = {
    "HOST": os.environ["WHOLESALE_MYSQL_HOST"],
    "PORT": os.environ["WHOLESALE_MYSQL_PORT"],
    "USER": os.environ["WHOLESALE_MYSQL_USER"],
    "PASSWORD": os.environ["WHOLESALE_MYSQL_PASSWORD"],
    "DBNAME": os.environ["WHOLESALE_MYSQL_DBNAME"],
}
