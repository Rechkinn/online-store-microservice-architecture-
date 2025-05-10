import psycopg2

from psycopg2.extras import RealDictCursor

connect = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="postgres",
    dbname="order_db",
    port="5432"
)

with connect:
    cursor = connect.cursor(cursor_factory=RealDictCursor)