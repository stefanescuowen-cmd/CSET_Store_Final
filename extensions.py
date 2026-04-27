from sqlalchemy import create_engine

conn_str = "mysql://root:cset155@localhost/store_db"
engine = create_engine(conn_str, pool_pre_ping=True)