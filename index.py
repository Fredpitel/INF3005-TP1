# coding=utf-8
from flask import Flask, render_template, g, request, redirect
from database import Database
from slugify import slugify
import datetime

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
    article = get_db().get_article(identifiant)
    try:
        return render_template(
            'article.html',
            article=article)
    except Exception as e:
        return page_inexistante(e)


@app.route('/rechercher', methods=['GET'])
def rechercher():
    articles = get_db().rechercher_articles(request.args['recherche'])
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
    article = get_db().get_article(identifiant)
    try:
        return render_template(
            'modifier.html',
            article=article)
    except Exception as e:
        return page_inexistante(e)


@app.route('/modifier', methods=['POST'])
def modifier():
    identifiant = request.form['identifiant']
    titre = request.form['titre']
    auteur = request.form['auteur']
    date = request.form['date']
    paragraphe = request.form['paragraphe']
    nouvel_identifiant = slugify(titre)

    if identifiant != nouvel_identifiant \
            and get_db().get_article(nouvel_identifiant) is not None:
        article = [None, titre, identifiant, auteur, date, paragraphe]
        return erreur_formulaire('modifier.html',
                                 article,
                                 u"Ce nom d'article existe déjà",
                                 400)

    article = get_db().modifier_article(identifiant,
                                        titre,
                                        paragraphe,
                                        nouvel_identifiant)
    try:
        return redirect("/article/{}".format(article[2]))
    except Exception:
        article = [None, titre, identifiant, auteur, date, paragraphe]
        return erreur_formulaire('modifier.html',
                                 article,
                                 "Erreur lors de la modification de l'article",
                                 500)


@app.route('/admin_nouveau')
def admin_nouveau():
    return render_template('admin_nouveau.html', article=None)


@app.route('/nouveau', methods=['POST'])
def nouveau():
    auteur = request.form['auteur']
    titre = request.form['titre']
    identifiant = slugify(request.form['titre'])
    paragraphe = request.form['paragraphe']
    date = request.form['date']
    article = [None, titre, identifiant, auteur, date, paragraphe]

    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return erreur_formulaire('admin_nouveau.html',
                                 article,
                                 u"Le format de la date doit être AAAA-MM-JJ",
                                 400)

    if get_db().get_article(identifiant) is not None:
        return erreur_formulaire('admin_nouveau.html',
                                 article,
                                 u"Ce nom d'article existe déjà",
                                 400)

    article = get_db().nouveau(auteur, titre, identifiant, paragraphe, date)
    try:
        return redirect("/article/{}".format(article[2]))
    except Exception:
        article = [None, titre, identifiant, auteur, date, paragraphe]
        return erreur_formulaire('admin_nouveau.html',
                                 article,
                                 "Erreur lors de la publication de l'article",
                                 500)


@app.errorhandler(404)
def page_inexistante(e):
    return render_template('404.html'), 404


def erreur_formulaire(template, article, msg_erreur, code_erreur):
    return render_template(
        template,
        article=article,
        erreur=msg_erreur
    ), code_erreur
