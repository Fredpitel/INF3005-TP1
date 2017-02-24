# coding=utf-8
class FormInputError(Exception):
    def __init__(self, template, article, message, code):
        self.template = template
        self.article = article
        self.message = message
        self.code = code
