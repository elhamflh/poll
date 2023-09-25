from typing import List
from psycopg2.extras import execute_values
from contextlib import contextmanager



vote=tuple[str,int]
poll=tuple[int,str,str]
PollResults=tuple[int,str,int,float] #SELECT_POLL_VOTE_DETAIL 
Options=tuple[int, str, int]

CREATE_POLLS = """CREATE TABLE IF NOT EXISTS polls
(id SERIAL PRIMARY KEY, title TEXT, owner_username TEXT);"""
CREATE_OPTIONS = """CREATE TABLE IF NOT EXISTS options
(id SERIAL PRIMARY KEY, option_text TEXT, poll_id INTEGER);"""
CREATE_VOTES = """CREATE TABLE IF NOT EXISTS votes
(username TEXT, option_id INTEGER, vote_timestamp INTEGER, FOREIGN KEY (option_id) REFERENCES options(id));"""


SELECT_POLL = "SELECT * FROM polls WHERE id = %s"
SELECT_RANDOM_VOTE= """SELECT * FROM VOTES WHERE option_id = %s ORDER BY RANDOM() LIMIT 1"""
SELECT_LATEST_POLL= '''SELECT * FROM poll
WHERE polls.id =(SELECT id FROM polls ORDER BY id  DECS LIMIT  1);'''
SELECT_POLL_VOTE_DETAIL="""SELECT 
options.id,
options.option_text,
COUNT(votes.option_id) AS VOTE_COUNT,
COUNT(votes.option_id) / SUM(COUNT(votes.option_id)) OVER() *100.0 AS VOTE_PERCENTAGE
FROM options
LEFT JOIN votes ON options.id = votes.option_id
where options.poll_id = %s
GROUP BY options.id; """
SELECT_ALL_POLLS = "SELECT * FROM polls;"
SELECT_POLL_OPTIONS = """SELECT * FROM options WHERE poll_id = %s;"""
SELECT_OPTIONS = """SELECT * FROM POLL WHERE id = %s;"""
SELECT_VOTES_FOR_OPTIONS = 'SELECT * FROM votes WHERE poll_id = %s;'

INSERT_POLL_RETURN_ID="INSERT INTO polls (title, owner_username) VALUES (%s,%s)RETURNING id;"
INSERT_OPTION_RETURN_ID = "INSERT INTO options (option_text, poll_id) VALUES %s;"
INSERT_VOTE = "INSERT INTO votes (username, option_id , vote_timestamp) VALUES (%s, %s , %s);"

@contextmanager
def get_cursor(connection):
    with connection:
        with connection.cursor() as cursor:

            yield cursor




#--polls--

def create_poll(connection, title:str , owner_username: str): 
    with get_cursor(connection) as cursor:
        cursor.execute(INSERT_POLL_RETURN_ID,(title,owner_username))

        poll_id = cursor.fetchone()[0]
        return poll_id
                
def create_tables(connection):
    with get_cursor(connection) as cursor:

        cursor.execute(CREATE_POLLS)
        cursor.execute(CREATE_OPTIONS)
        cursor.execute(CREATE_VOTES)


def get_polls(connection)-> List[poll]: #thats a list of str because we have diffrent options.
    with get_cursor(connection) as cursor:

        cursor.execute(SELECT_ALL_POLLS)
        return cursor.fetchall()

def get_poll(connection, poll_id : int) -> poll:
    with get_cursor(connection) as cursor:

        cursor.execute(SELECT_POLL, (poll_id,))
        return cursor.fetchone()
    

def get_latest_poll(connection)-> poll:
    with get_cursor(connection) as cursor:

        cursor.execute(SELECT_LATEST_POLL)
        return cursor.fetchone()

#--option--

def get_poll_options(connection, poll_id: int)-> List[Options]:
    with get_cursor(connection) as cursor:

        cursor.execute(SELECT_POLL_OPTIONS, (poll_id,))
        return cursor.fetchall()
        
def get_option(connection, option_id: int) -> Options:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_OPTIONS,(option_id,))

def add_option(connection, option_text, option_id):
    with get_cursor(connection) as cursor:

        cursor.execute(INSERT_OPTION_RETURN_ID, (option_text,option_id,))
        option_id = cursor.fetchone() [0]
        return option_id

#--votes--

def get_votes_for_option(connection,option_id)-> List[vote]:
    with get_cursor(connection) as cursor:

        cursor.execute(SELECT_VOTES_FOR_OPTIONS, (option_id,))
        return cursor.fetchone()

def add_poll_vote(connection, username: str, vote_timestamp: float, option_id: int):
    with get_cursor(connection) as cursor:
        cursor.execute(INSERT_VOTE, (username, option_id, vote_timestamp))