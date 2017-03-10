# coding=utf-8
import re
import datetime
from flask import Flask, render_template, g, request, redirect, abort
from database import Database
from article import Article
from erreur_formulaire import FormInputError

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
    articles = get_db().get_derniers_articles()
    return render_template('acceuil.html',
                           articles=articles)


@app.route('/article/<identifiant>')
def page_article(identifiant):
    try:
        article = get_db().get_article(identifiant)
        return render_template('article.html',
                               article=article)
    except:
        abort(404)


@app.route('/rechercher', methods=['GET'])
def rechercher():
    articles = get_db().rechercher_articles(
        request.args['recherche'].encode('utf-8'))
    return render_template('recherche.html',
                           recherche=request.args['recherche'],
                           articles=articles)


@app.route('/admin')
def admin():
    articles = get_db().get_all_articles()
    return render_template('admin.html',
                           articles=articles)


@app.route('/modifier/<identifiant>')
def modifier_article(identifiant):
    try:
        article = get_db().get_article(identifiant)
        return render_template('modifier.html',
                               article=article)
    except:
        abort(404)


@app.route('/modifier', methods=['POST'])
def modifier():
    article_original = get_db().get_article(request.form['identifiant'])
    article_modifie = article_from_form(request.form)

    if article_modifie.titre != article_original.titre:
        valider_unique(article_modifie, 'modifier.html')

    try:
        get_db().modifier_article(article_modifie,
                                  article_original.identifiant)
        return redirect("/admin")
    except:
        raise FormInputError('modifier.html',
                             article_modifie,
                             "Erreur lors de la modification de l'article",
                             500)


@app.route('/admin_nouveau')
def admin_nouveau():
    return render_template('admin_nouveau.html',
                           article=None)


@app.route('/nouveau', methods=['POST'])
def nouveau():
    article = article_from_form(request.form)
    valider_identifiant(article)
    valider_date(article)
    valider_unique(article, 'admin_nouveau.html')

    try:
        get_db().nouveau(article)
        return redirect("/admin")
    except:
        raise FormInputError('admin_nouveau.html',
                             article,
                             "Erreur lors de la publication de l'article",
                             500)


def article_from_form(formulaire):
    return Article([None,
                    formulaire['titre'],
                    formulaire['identifiant'].lower(),
                    formulaire['auteur'],
                    formulaire['date'],
                    formulaire['paragraphe']])


def valider_identifiant(article):
    if re.search('[^a-zA-Z0-9-_]', article.identifiant) is not None:
        raise FormInputError('admin_nouveau.html',
                             article,
                             u"L'identifiant ne doit contenir que des caractères alphanumériques",
                             400)


def valider_date(article):
    try:
        datetime.datetime.strptime(article.date, "%Y-%m-%d")
    except ValueError:
        raise FormInputError('admin_nouveau.html',
                             article,
                             u"Le format de la date doit être AAAA-MM-JJ",
                             400)


def valider_unique(article, template):
    try:
        get_db().get_article(article.identifiant)
    except:
        return
    raise FormInputError(template,
                         article,
                         u"Ce nom d'article existe déjà",
                         400)


@app.errorhandler(404)
def page_inexistante(e):
    return render_template('404.html'), 404


@app.errorhandler(FormInputError)
def erreur_formulaire(e):
    return render_template(e.template,
                           article=e.article,
                           erreur=e.message,
                           ), e.code
