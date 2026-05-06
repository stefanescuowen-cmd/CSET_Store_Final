from sqlalchemy import create_engine

conn_str = "mysql://root:cset155@localhost/store_db"
engine = create_engine(conn_str, echo=True, pool_pre_ping=True)
app_conn = engine.connect()


def rollback_app_connection():
    if app_conn.in_transaction():
        app_conn.rollback()
