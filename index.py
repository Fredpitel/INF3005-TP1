# coding=utf-8
from flask import Flask, render_template, g, request, redirect
from database import Database
import datetime
import re

app = Flask(__name__, static_url_path="", static_folder="static")
_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_underscore_re = re.compile(r'[-\s]+')

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
    return render_template('acceuil.html', articles=articles)


@app.route('/article/<identifiant>')
def page_article(identifiant):
    article = get_db().get_article(identifiant)
    try:
        return render_template('article.html', article=article)
    except Exception as e:
        return page_inexistante(e)


@app.route('/rechercher', methods=['GET'])
def rechercher():
    articles = get_db().rechercher_articles(request.args['recherche'])
    return render_template('recherche.html', articles=articles)


@app.route('/admin')
def admin():
    articles = get_db().get_all_articles()
    return render_template('admin.html', articles=articles)


@app.route('/modifier/<identifiant>')
def modifier_article(identifiant):
    article = get_db().get_article(identifiant)
    try:
        return render_template('modifier.html', article=article)
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

    if get_db().get_article(nouvel_identifiant) is not None:
        article = [None, titre, identifiant, auteur, date, paragraphe]
        return render_template('modifier.html',
                        article=article,
                        erreur=u"Ce nom d'article existe déjà"), 400

    article = get_db().modifier_article(identifiant,
                                        titre,
                                        paragraphe,
                                        nouvel_identifiant)
    try:
        return redirect("/article/{}".format(article[0][2]))
    except Exception as e:
        article = get_db().get_article(request.form['identifiant'])
        return render_template('modifier.html',
                               article=article,
                               erreur="Erreur lors de la modification de l'article"), 500


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

    if get_db().get_article(identifiant) is not None:
        article = [None, titre, identifiant, auteur, date, paragraphe]
        return render_template('admin_nouveau.html',
                               article=article,
                               erreur=u"Ce nom d'article existe déjà"), 400

    article = get_db().nouveau(auteur, titre, identifiant, paragraphe, date)
    try:
        return redirect("/article/{}".format(article[0][2]))
    except Exception as e:
        article = [None, titre, identifiant, auteur, date, paragraphe]
        return render_template('admin_nouveau.html',
                               article=article,
                               erreur="Erreur lors de la publication de l'article"), 500


@app.errorhandler(404)
def page_inexistante(e):
    return render_template('404.html'), 404


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to underscore.

    From Django's "django/template/defaultfilters.py".
    """
    import unicodedata
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(_slugify_strip_re.sub('', value).strip().lower())
    return _slugify_underscore_re.sub('_', value)


@app.template_filter('slugify')
def _slugify(string):
    if not string:
        return ""
    return slugify(string)
