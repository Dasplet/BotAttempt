import sqlite3
import pathlib
import os

from connection_pool import ConnectionPool

class SQLiteConnector:
    db_path: str
    pool: ConnectionPool

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.pool = ConnectionPool(db_path)
    
    def create_tables(self):
        # pass
        conn = self.pool.get_connection()

        cursor = conn.cursor()

        series_table = '''
            CREATE TABLE IF NOT EXISTS series (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );
            '''

        characters_table = '''
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                series_id INTEGER NOT NULL,
                FOREIGN KEY(series_id) REFERENCES series(id)
            );
            '''

        questions_table = '''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id TEXT NOT NULL,
                question TEXT NOT NULL,
                FOREIGN KEY(character) REFERENCES characters(id)
            );
            '''

        answers_table = '''
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                answer TEXT NOT NULL,
                valid BOOLEAN NOT NULL,
                FOREIGN KEY(question_id) REFERENCES questions(id)
            );
            '''

        # can make this an auto tag -> worker_table = "code, print, edition, wishlist, quality, effort, burnvalue, series id, charecter id"

        create_table_query = series_table + questions_table + answers_table + characters_table
        cursor.execute(create_table_query)
        conn.commit()


        self.pool.release_connection(conn)


    def insert_series(self, series_name: str):
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            insert_query = '''
                INSERT INTO series (name)
                VALUES (?);
                '''
            
            cursor.execute(insert_query, (series_name,))
            conn.commit()

    def insert_character(self, name: str, series_name: str):
            with self.get_connection() as conn:  # Using the connection from the pool
                cursor = conn.cursor()
                insert_query = '''
                    INSERT INTO characters (name, series_id)
                    VALUES (?, (SELECT id FROM series WHERE name = ?));
                '''
                cursor.execute(insert_query, (name, series_name))
                conn.commit()


    def insert_question(self, question: str, character_name: str):
        with self.get_connection() as conn:  # Using the connection from the pool
            cursor = conn.cursor()
            insert_query = '''
                INSERT INTO questions (character_id, question)
                VALUES ((SELECT id from characters WHERE name = ?), ?);
            '''
            cursor.execute(insert_query, (character_name, question))
            conn.commit()

    def insert_answer(self, question_id: int, answer: str, valid: bool):
        with self.get_connection() as conn:  # Using the connection from the pool
            cursor = conn.cursor()
            insert_query = '''
                INSERT INTO answers (question_id, answer, valid)
                VALUES (?, ?, ?);
            '''
            cursor.execute(insert_query, (question_id, answer, valid))
            conn.commit()

    def update_question(self, question_id: int, new_question: str):
        with self.get_connection() as conn:  # Using the connection from the pool
            cursor = conn.cursor()
            update_query = '''
                UPDATE questions 
                SET question = ? 
                WHERE id = ?;
            '''
            cursor.execute(update_query, (new_question, question_id))
            conn.commit()

    def update_answer(self, answer_id: int, new_answer: str, new_valid: bool):
        with self.get_connection() as conn:  # Using the connection from the pool
            cursor = conn.cursor()
            update_query = '''
                UPDATE answers 
                SET answer = ?, valid = ? 
                WHERE id = ?;
            '''
            cursor.execute(update_query, (new_answer, new_valid, answer_id))
            conn.commit()


    def delete_answer(self, answer_id: int):
        with self.get_connection() as conn:  # Using the connection from the pool
            cursor = conn.cursor()
            delete_query = '''
                DELETE FROM answers 
                WHERE id = ?;
            '''
            cursor.execute(delete_query, (answer_id,))
            conn.commit()