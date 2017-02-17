import sqlite3


class Database:
    def __init__(self):
        self.connection = None

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect("db/article.db")
        return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()

    def get_articles(self, date):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM article WHERE date_publication <= '{}' LIMIT 5;".format(date))
        return cursor.fetchall()

    def rechercher_articles(self, recherche):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM article "
                       "WHERE titre LIKE '%{}%' OR paragraphe LIKE '%{}%';".format(recherche, recherche))
        return cursor.fetchall()

    def get_article(self, identifier):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM article WHERE identifiant ='{}';".format(identifier))
        return cursor.fetchall()