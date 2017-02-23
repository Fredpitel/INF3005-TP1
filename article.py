# coding=utf-8


class Article:
    def __init__(self, row):
        self.titre = row[1]
        self.identifiant = row[2]
        self.auteur = row[3]
        self.date = row[4]
        self.paragraphe = row[5]
