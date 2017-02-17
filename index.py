from flask import Flask, render_template, g, request, redirect
from database import Database
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
    return render_template('acceuil.html', articles=articles)


@app.route('/rechercher', methods=['GET'])
def rechercher():
    articles = get_db().rechercher_articles(request.args['recherche'])
    return render_template('recherche.html', articles=articles)


@app.route('/article/<identifier>')
def page_article(identifier):
    article = get_db().get_article(identifier)
    if not article:
        page_inexistante(HTTPException(404))
    return render_template('article.html', article=article[0])

@app.errorhandler(404)
def page_inexistante(e):
    return render_template('404.html'), 404