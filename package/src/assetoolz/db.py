from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from functools import wraps
import os

db_session = None

Model = declarative_base()


def entry_point(func):
    @wraps(func)
    def internal(*args, **kwargs):
        result = None
        cache_db_path = os.path.join(args[0].cache_path, "cache.db")
        engine = create_engine("sqlite:///" + cache_db_path,
                               convert_unicode=True)
        global db_session
        db_session = scoped_session(sessionmaker(autocommit=False,
                                                 autoflush=False,
                                                 bind=engine))
        global Model
        Model.query = db_session.query_property()
        from . import models
        Model.metadata.create_all(bind=engine)
        try:
            result = func(*args, **kwargs)
        finally:
            db_session.remove()
        return result

    return internal
