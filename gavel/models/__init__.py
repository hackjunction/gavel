import gavel.crowd_bt as crowd_bt
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy.exc
import psycopg2.errors

db = SQLAlchemy(engine_options={"isolation_level": "SERIALIZABLE"})

from gavel.models.annotator import Annotator, ignore_table
from gavel.models.item import Item, view_table
from gavel.models.decision import Decision
from gavel.models.setting import Setting

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import desc

def with_retries(tx_func):
    '''
    Keep retrying a function that involves a database transaction until it
    succeeds.

    This only retries due to serialization failures; all other types of
    exceptions are re-raised.
    '''
    while True:
        try:
            tx_func()
        except sqlalchemy.exc.OperationalError as err:
            if not isinstance(err.orig, psycopg2.errors.SerializationFailure):
                raise
            db.session.rollback()
        else:
            break
