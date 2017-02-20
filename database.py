import sqlite3


class Database:
    def __init__(self):
        self.connection = None

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect("C:\\INF3005\\TP1\\db\\article.db")
        return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()

    def get_all_articles(self):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM article;")
        return cursor.fetchall()

    def get_articles(self, date):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM article "
                       "WHERE date_publication <= '{}' "
                       "ORDER BY date_publication DESC LIMIT 5;".format(date))
        return cursor.fetchall()

    def rechercher_articles(self, recherche):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM article "
                       "WHERE titre LIKE '%{}%' OR paragraphe LIKE '%{}%';".format(recherche, recherche))
        return cursor.fetchall()

    def get_article(self, identifiant):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM article "
                       "WHERE identifiant ='{}';".format(identifiant))
        return cursor.fetchone()

    def modifier_article(self, identifiant, titre, paragraphe, nouvel_identifiant):
        connection = self.get_connection()
        cursor = self.get_connection().cursor()
        try:
            cursor.execute("UPDATE article SET titre = ?, paragraphe = ?, identifiant = ?"
                           "WHERE identifiant = ?;", (titre, paragraphe, nouvel_identifiant, identifiant))
            connection.commit()
            return self.get_article(nouvel_identifiant)
        except Exception as e:
            return None

    def nouveau(self, auteur, titre, identifiant, paragraphe, date):
        connection = self.get_connection()
        cursor = self.get_connection().cursor()
        try:
            cursor.execute("INSERT INTO article "
                           "VALUES (null, ?, ?, ?, ?, ?)",
                           (titre, identifiant, auteur, date, paragraphe))
            connection.commit()
            return self.get_article(identifiant)
        except Exception as e:
            return None
