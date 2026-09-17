import os
from contextlib import contextmanager

import psycopg2
import psycopg2.extras

DATABASE_URL  = os.environ.get("DATABASE_URL", "postgresql:///rematch")

@contextmanager
def cursor():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor(cursor_factory= psycopg2.extras.RealDictCursor) as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_schema(path: str = "schema.sql") -> None:
    with open(path) as fh, cursor() as cur:
        cur.execute(fh.read())