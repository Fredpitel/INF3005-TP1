# coding: utf8

import datetime

def filtrer_par_date(articles):
    for article in articles:
        if article.date > datetime.date.today().isoformat():
            articles.remove(article)

    return articles


def article_from_form(formulaire):
    return Article([None,
                    formulaire['titre'],
                    formulaire['identifiant'].lower(),
                    formulaire['auteur'],
                    formulaire['date'],
                    formulaire['paragraphe']])


def valider_identifiant(article):
    if re.search('[^a-z0-9-_]', article.identifiant) is not None:
        raise FormInputError('admin_nouveau.html',
                             article,
                             u"L'identifiant ne peut contenir que des caractères alphanumériques.",
                             400)


def valider_date(article):
    try:
        datetime.datetime.strptime(article.date, "%Y-%m-%d")
    except ValueError:
        raise FormInputError('admin_nouveau.html',
                             article,
                             u"Le format de la date doit être AAAA-MM-JJ.",
                             400)


def valider_unique(article, template):
    try:
        get_db().get_article(article.identifiant)
    except:
        return
    raise FormInputError(template,
                         article,
                         u"Cet identifiant d'article existe déjà.",
                         400)