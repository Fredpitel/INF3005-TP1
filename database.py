# coding=utf-8
import sqlite3
from article import Article

PATH_TO_DB = "C:\\INF3005\\TP1\\db\\article.db"


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

    def get_all_articles(self):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM article;")
        return [Article(row) for row in cursor.fetchall()]

    def get_articles(self, date):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM article "
                       "WHERE date_publication <= '{}' "
                       "ORDER BY date_publication DESC LIMIT 5;".format(date))
        return [Article(row) for row in cursor.fetchall()]

    def rechercher_articles(self, recherche):
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM article "
                       "WHERE titre LIKE '%{}%' OR paragraphe LIKE '%{}%';"
                       .format(recherche, recherche))
        return [Article(row) for row in cursor.fetchall()]

    def get_article(self, identifiant):
        print identifiant
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT * FROM article "
                       "WHERE identifiant ='{}';".format(identifiant))
        try:
            return Article(cursor.fetchone())
        except:
            return None

    def modifier_article(self, article_modifie, id_original):
        connection = self.get_connection()
        cursor = self.get_connection().cursor()
        cursor.execute("UPDATE article "
                       "SET titre = ?, paragraphe = ?, identifiant = ?"
                       "WHERE identifiant = ?;",
                       (article_modifie.titre, article_modifie.paragraphe, article_modifie.identifiant, id_original))
        connection.commit()

    def nouveau(self, article):
        connection = self.get_connection()
        cursor = self.get_connection().cursor()
        cursor.execute("INSERT INTO article "
                       "VALUES (null, ?, ?, ?, ?, ?)",
                       (article.titre, article.identifiant, article.auteur, article.date, article.paragraphe))
        connection.commit()
