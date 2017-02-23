# coding=utf-8
class ErreurFormulaire(Exception):
    def __init__(self, template, article, message, code):
        self.template = template
        self.article = article
        self.message = message
        self.code = code
