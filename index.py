# coding=utf-8
from flask import Flask, render_template, g, request, redirect
from database import Database
import datetime
import urllib
from article import Article

app = Flask(__name__, static_url_path="", static_folder="static")


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        g._database = Database()
    return g._database


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()


@app.route('/')
def page_accueil():
    articles = get_db().get_articles(datetime.date.today().isoformat())
    return render_template(
        'acceuil.html',
        articles=articles)


@app.route('/article/<identifiant>')
def page_article(identifiant):
    article = get_db().get_article(urllib.quote(identifiant.encode('utf-8')))
    if article is not None:
        return render_template(
            'article.html',
            article=article)

    return page_inexistante()


@app.route('/rechercher', methods=['GET'])
def rechercher():
    articles = get_db().rechercher_articles(request.args['recherche'].encode('utf-8'))
    return render_template(
        'recherche.html',
        articles=articles)


@app.route('/admin')
def admin():
    articles = get_db().get_all_articles()
    return render_template(
        'admin.html',
        articles=articles)


@app.route('/modifier/<identifiant>')
def modifier_article(identifiant):
    article = get_db().get_article(urllib.quote(identifiant.encode('utf-8')))
    try:
        return render_template(
            'modifier.html',
            article=article)
    except:
        return page_inexistante()


@app.route('/modifier', methods=['POST'])
def modifier():
    article_original = get_db().get_article(request.form['identifiant'])
    article_modifie = article_from_form(request.form)

    if article_modifie.titre != article_original.titre \
            and get_db().get_article(article_modifie.identifiant) is not None:
        return erreur_formulaire('admin_nouveau.html',
                                 article_modifie,
                                 u"Ce nom d'article existe déjà",
                                 400)

    try:
        get_db().modifier_article(article_modifie, article_original.identifiant)
        return redirect("/article/{}".format(article_modifie.identifiant))
    except:
        return erreur_formulaire('modifier.html',
                                 article_modifie,
                                 "Erreur lors de la modification de l'article",
                                 500)


@app.route('/admin_nouveau')
def admin_nouveau():
    return render_template('admin_nouveau.html', article=None)


@app.route('/nouveau', methods=['POST'])
def nouveau():
    article = article_from_form(request.form)

    try:
        datetime.datetime.strptime(article.date, "%Y-%m-%d")
    except ValueError:
        return erreur_formulaire('admin_nouveau.html',
                                 article,
                                 u"Le format de la date doit être AAAA-MM-JJ",
                                 400)

    if get_db().get_article(article.identifiant) is not None:
        return erreur_formulaire('admin_nouveau.html',
                                 article,
                                 u"Ce nom d'article existe déjà",
                                 400)

    try:
        get_db().nouveau(article)
        return redirect("/article/{}".format(article.identifiant))
    except:
        return erreur_formulaire('admin_nouveau.html',
                                 article,
                                 "Erreur lors de la publication de l'article",
                                 500)


@app.errorhandler(404)
def page_inexistante():
    return render_template('404.html'), 404


def erreur_formulaire(template, article, msg_erreur, code_erreur):
    return render_template(
        template,
        article=article,
        erreur=msg_erreur
    ), code_erreur


def article_from_form(formulaire):
    return Article([None,
                    formulaire['titre'],
                    urllib.quote(formulaire['titre'].encode('utf-8')),
                    formulaire['auteur'],
                    formulaire['date'],
                    formulaire['paragraphe']])
