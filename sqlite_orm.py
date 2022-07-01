import sqlalchemy
from sqlalchemy import ForeignKey, Column, Integer, Float, String, Date, select, update, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship
from sqlalchemy.engine import Engine


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


sqlite_engine = sqlalchemy.create_engine(f"sqlite:///eNelayan.db",
                                         poolclass=sqlalchemy.pool.SingletonThreadPool, echo=True, future=True)
event.listen(sqlite_engine, 'connect', set_sqlite_pragma)
Base = declarative_base()