from flask import Flask, render_template, g, request, redirect
from database import Database
import datetime
import urllib

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


@app.route('/article/<identifiant>')
def page_article(identifiant):
    article = get_db().get_article(identifiant)
    try:
        return render_template('article.html', article=article[0])
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
        return render_template('modifier.html', article=article[0])
    except Exception as e:
        return page_inexistante(e)


@app.route('/modifier', methods=['POST'])
def modifier():
    article = get_db().modifier_article(request.form['identifiant'], request.form['titre'], request.form['paragraphe'])
    try:
        return redirect("/article/{}".format(article[0][2]))
    except Exception as e:
        article = get_db().get_article(request.form['identifiant'])
        return render_template('modifier.html', article=article[0], erreur="Erreur lors de la modification de l'article")


@app.route('/admin_nouveau')
def admin_nouveau():
    return render_template('admin_nouveau.html')


@app.route('/nouveau', methods=['POST'])
def nouveau():
    auteur = request.form['auteur']
    titre = request.form['titre']
    identifiant = urllib.quote_plus(unicode(request.form['titre'], "utf-8"))
    paragraphe = request.form['paragraphe']
    date = request.form['date']
    article = get_db().nouveau(auteur, titre, identifiant, paragraphe, date)
    try:
        return redirect("/article/{}".format(article[0][2]))
    except Exception as e:
        return render_template('admin_nouveau.html',
                               erreur="Erreur lors de la publication de l'article",
                               auteur=auteur,
                               titre=titre,
                               paragraphe=paragraphe,
                               date=date)


@app.errorhandler(404)
def page_inexistante(e):
    return render_template('404.html'), 404
