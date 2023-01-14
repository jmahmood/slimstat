import datetime
from pprint import pprint
from typing import TypedDict
import sqlite3


class WeightData(TypedDict):
    mean: float
    median: int
    stdev: float
    samples: int
    measurement_datetime: datetime.datetime


def save_data(db: sqlite3.Connection, weight_data: WeightData):
    db.execute(
        'INSERT INTO weight_log (measurement_datetime, measurement_datetime_display, mean, median, stdev, samples) '
        'VALUES (julianday(?), ?, ?, ?, ?, ?)',
        [
            weight_data['measurement_datetime'],
            weight_data['measurement_datetime'],
            weight_data['mean'],
            weight_data['median'],
            weight_data['stdev'],
            weight_data['samples'],
        ]
    )
    db.commit()


def get_morning_data_from(db: sqlite3.Connection, date: datetime.date):
    pass


def get_data_from(db: sqlite3.Connection, from_date: datetime, until_date: datetime):
    cur = db.cursor()
    q = """SELECT mean, median, stdev, samples, measurement_datetime_display from weight_log
        WHERE measurement_datetime >= julianday(?) AND measurement_datetime <= julianday(?)"""
    cur.execute(q, [from_date, until_date])
    return cur.fetchall()


# Retrieve the first data point, then the data for the past month, then the data for the past week.
def get_data_range(db: sqlite3.Connection, start_date: datetime, end_date: datetime):
    cur = db.cursor()
    q = """SELECT mean, median, stdev, samples, measurement_datetime_display from weight_log
        WHERE measurement_datetime BETWEEN julianday(?) AND julianday(?)"""
    cur.execute(q, [start_date, end_date])
    return cur.fetchall()


# Retrieve the first data point, then the data for the past month, then the data for the past week.
def get_data_range_mean(db: sqlite3.Connection, start_date: datetime, end_date: datetime):
    cur = db.cursor()
    cur.row_factory = lambda cursor, row: row[0]
    q = """SELECT mean from weight_log
        WHERE measurement_datetime BETWEEN julianday(?) AND julianday(?)"""
    cur.execute(q, [start_date, end_date])
    return cur.fetchall()


# Retrieve the first data point, then the data for the past month, then the data for the past week.
def get_monthly_data(db: sqlite3.Connection, end_date: datetime):
    cur = db.cursor()
    q = """SELECT mean, median, stdev, samples, measurement_datetime_display from weight_log
        WHERE measurement_datetime <= julianday(?)"""
    cur.execute(q, [end_date])
    return cur.fetchall()


# Retrieve the first data point, then the data for the past month, then the data for the past week.
def get_first_data(db: sqlite3.Connection):
    cur = db.cursor()
    q = """SELECT mean, median, stdev, samples, measurement_datetime_display from weight_log
        order by measurement_datetime limit 1"""
    cur.execute(q)
    return cur.fetchone()


def create_database_table(db: sqlite3.Connection):
    q = """create table if not exists weight_log
(
    measurement_datetime         REAL    not null,
    measurement_datetime_display text,
    mean                          integer not null,
    median                        integer not null,
    stdev                        integer not null,
    samples                     integer not null,
    id                           integer not null
        constraint weight_log_pk
            primary key autoincrement
);"""

    q2 = """create index if not exists main.weight_log_measurement_datetime_index
    on weight_log (measurement_datetime);"""
    db.execute(q)
    db.execute(q2)
    db.commit()


if __name__ == '__main__':
    # delete file.

    weight_data_database = sqlite3.Connection(":memory:", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    data: WeightData = {
        "mean": 100.5,
        "median": 100,
        "stdev": 0.5,
        "samples": 20,
        "measurement_datetime": datetime.datetime.now()
    }
    create_database_table(weight_data_database)
    save_data(weight_data_database, data)
    pprint(get_first_data(weight_data_database))
    pprint(get_monthly_data(weight_data_database, datetime.datetime.now()))
