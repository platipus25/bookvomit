import csv
import http.client
import urllib
import json
import time
import logging
import sqlite3
import difflib

from book_data import get_book

logger = logging.getLogger(__name__)

logging.basicConfig(filename='vomit.log', level=logging.INFO)

db_conn = sqlite3.connect('books.db')


schema = ["""CREATE TABLE books
(
    key TEXT,
    title text NOT NULL,
    physical_format text,
    number_of_pages integer,
    first_sentence text,
    physical_dimensions text,
    weight real,
    id_project_gutenberg integer,
    CONSTRAINT books_key PRIMARY KEY (key)
)"""]

def validate_schema(conn, expected_schema):
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_schema WHERE type='table'")
    actual_schema = cursor.fetchall()
    actual_schema = [sql for (sql,) in actual_schema]

    for stmt in expected_schema:
        if stmt not in actual_schema:
            logger.error(f"Expected statement not found in actual schema: {stmt}")

            closest_matches = difflib.get_close_matches(stmt, actual_schema)
            if closest_matches:
                logger.info("Did you mean one of these?")
                for match in closest_matches:
                    diff = difflib.unified_diff(
                            stmt.splitlines(keepends=True),
                            match.splitlines(keepends=True),
                            )
                    logger.info(f"  - {''.join(diff)}")
                    logger.info(f"'{stmt}' '{match}'")
            return False

    logger.info("Schema validation passed")
    return True

ok = validate_schema(db_conn, schema)
if not ok:
    print("Schema did not validate, check log and fix")
    exit()

cur = db_conn.cursor()

#cur.execute(schema[0])

def add_book(title):

    book = get_book(title)
    print(book)

    cur.execute("INSERT INTO books VALUES(:key, :title, :physical_format, :number_of_pages, :first_sentence, :physical_dimensions, :weight, :id_project_gutenberg)", book)
    db_conn.commit()


add_book("The Great Gatsby")

words_per_minute = 120
word_reading_period = 1.0 / (words_per_minute / 60.0)

words = []#book["contents"].split()
for word in words:
    print(word)
    time.sleep(word_reading_period)
