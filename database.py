# coding=utf-8
import sqlite3
from article import Article

PATH_TO_DB = 'C:\INF3005\TP1\db\cms.db'


class Database:
    def __init__(self):
        self.connection = None

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect(PATH_TO_DB)
        return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()

    def get_article(self, identifiant):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM article "
                       "WHERE identifiant = ?;",
                       (identifiant,))
        return Article(cursor.fetchone())

    def get_all_articles(self):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM article;")
        return [Article(row) for row in cursor.fetchall()]

    def get_derniers_articles(self, date):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM article "
                       "WHERE date_publication <= ? "
                       "ORDER BY date_publication DESC LIMIT 5;",
                       (date,))
        return [Article(row) for row in cursor.fetchall()]

    def rechercher_articles(self, recherche):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM article "
                       "WHERE titre LIKE ? OR paragraphe LIKE ?;",
                       (recherche, recherche))
        return [Article(row) for row in cursor.fetchall()]

    def modifier_article(self, article_modifie, id_original):
        connection = self.get_connection()
        cursor = self.get_connection().cursor()
        cursor.execute("UPDATE article "
                       "SET titre = ?, paragraphe = ?, identifiant = ?"
                       "WHERE identifiant = ?;",
                       (article_modifie.titre,
                        article_modifie.paragraphe,
                        article_modifie.identifiant,
                        id_original))
        connection.commit()

    def nouveau(self, article):
        connection = self.get_connection()
        cursor = self.get_connection().cursor()
        cursor.execute("INSERT INTO article "
                       "VALUES (null, ?, ?, ?, ?, ?);",
                       (article.titre,
                        article.identifiant,
                        article.auteur,
                        article.date,
                        article.paragraphe))
        connection.commit() 

    def save_session(self, identifiant, username):
        connection = self.get_connection()
        cursor = self.get_connection().cursor()
        cursor.execute("INSERT INTO session "
                       "VALUES (null, ?, ?);",
                       (identifiant, username))
        connection.commit()

    def delete_session(self, identifiant):
        connection = self.get_connection()
        cursor = self.get_connection().cursor()
        cursor.execute("DELETE FROM session "
                       "WHERE id = ?;", 
                       (identifiant,))
        connection.commit()

    def get_username(self, identifiant):
        cursor = self.get_connection().cursor()
        cursor.execute(("SELECT username FROM session "
                        "WHERE id_session = ?;"),
                       (identifiant,))
        return cursor.fetchone()[0]

    def get_user_infos(self, username):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT salt, hash FROM user "
                       "WHERE username = ?;", 
                       (username,))
        return cursor.fetchone()

    def get_email(self, username):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT email FROM user "
                       "WHERE username = ?;",
                       (username,))
        return cursor.fetchone()[0]

    def save_jeton_mdp(self, username, jeton, timestamp):
        connection = self.get_connection()
        cursor = self.get_connection().cursor()
        cursor.execute("INSERT INTO jeton_mdp "
                       "VALUES (null, ?, ?, ?);",
                       (username, jeton, timestamp))
        connection.commit()

    def delete_jeton_mdp(self, username):
        connection = self.get_connection()
        cursor = self.get_connection().cursor()
        cursor.execute("DELETE FROM jeton_mdp "
                       "WHERE username = ?",
                       (username,))
        connection.commit()

    def get_jeton_mdp(self, username):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT jeton, time_jeton FROM jeton_mdp "
                       "WHERE username = ?;",
                       (username,))
        return cursor.fetchone()

    def modifier_mdp(self, username, password):
        connection = self.get_connection()
        cursor = self.get_connection().cursor()
        cursor.execute("UPDATE user "
                       "SET hash = ? "
                       "WHERE username = ?;",
                       (password, username))
        connection.commit()

    def save_jeton_invitation(self, email, jeton, timestamp):
        connection = self.get_connection()
        cursor = self.get_connection().cursor()
        cursor.execute("INSERT INTO jeton_invitation "
                       "VALUES (null, ?, ?, ?);",
                       (email, jeton, timestamp))
        connection.commit()

    def get_jeton_invitation(self, email):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT jeton, time_jeton FROM jeton_invitation "
                       "WHERE email = ?;",
                       (email,))
        return cursor.fetchone()

    def delete_jeton_invitation(self, email):
        connection = self.get_connection()
        cursor = self.get_connection().cursor()
        cursor.execute("DELETE FROM jeton_invitation "
                       "WHERE email = ?",
                       (email,))
        connection.commit()

    def create_user(self, username, email, salt, password):
        connection = self.get_connection()
        cursor = self.get_connection().cursor()
        cursor.execute("INSERT INTO user "
                       "VALUES (null, ?, ?, ?, ?);",
                       (username, email, salt, password))
        connection.commit()
