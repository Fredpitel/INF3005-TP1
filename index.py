# coding=utf-8

from flask import Flask, render_template, g, request, redirect, abort, session
from database import Database
from article import Article
from erreur_formulaire import FormInputError
from authentification import authentication_required
from validations_formulaire import *
import hashlib
import uuid

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
    username = None
    try:
        print session['id']
    except:
        pass
    if 'id' in session:
        username = get_db().get_username(session['id'])

    date = datetime.date.today().isoformat()
    articles = get_db().get_derniers_articles(date)
    return render_template('acceuil.html',
                           articles=articles,
                           username=username)


@app.route('/article/<identifiant>')
def page_article(identifiant):
    try:
        article = get_db().get_article(identifiant)
        article = filtrer_par_date([article])[0]
        return render_template('article.html',
                               article=article)
    except:
        abort(404)


@app.route('/rechercher', methods=['GET'])
def rechercher():
    articles = get_db().rechercher_articles(
        request.args['recherche'].encode('utf-8'))

    articles = filtrer_par_date(articles)
    return render_template('recherche.html',
                           recherche=request.args['recherche'],
                           articles=articles)


@app.route('/admin')
@authentication_required
def admin():
    articles = get_db().get_all_articles()
    return render_template('admin.html',
                           articles=articles)


@app.route('/modifier/<identifiant>')
@authentication_required
def modifier_article(identifiant):
    try:
        article = get_db().get_article(identifiant)
        return render_template('modifier.html',
                               article=article)
    except:
        abort(404)


@app.route('/modifier', methods=['POST'])
@authentication_required
def modifier():
    #article_original = get_db().get_article(request.form['identifiant'])
    article = article_from_form(request.form)

    if article.identifiant != request.form['identifiant']:
        valider_unique(article, 'modifier.html')

    try:
        get_db().modifier_article(article, request.form['identifiant'])
        return redirect("/admin")
    except:
        raise FormInputError('modifier.html',
                             article,
                             "Erreur lors de la modification de l'article.",
                             500)


@app.route('/admin_nouveau')
@authentication_required
def admin_nouveau():
    return render_template('admin_nouveau.html',
                           article=None)


@app.route('/nouveau', methods=['POST'])
@authentication_required
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
                             "Erreur lors de la publication de l'article.",
                             500)


@app.route('/login_form')
def login_form():
    return render_template('login.html',
                           referer=request.headers["Referer"])


@app.route('/login', methods=['POST'])
def login():
    try:
        user = get_db().get_user_infos(request.form['username'])
        hashed_password = hashlib.sha512(request.form['password'] + user[0]).hexdigest()

        if hashed_password == user[1]:
            id_session = uuid.uuid4().hex
            get_db().save_session(id_session, username)
            session['id'] = id_session

        return redirect('/')
    except Exception as e:
        print e
        raise FormInputError('login.html',
                             None,
                             "Nom d'usager ou mot de passe incorrect.",
                             403)


@app.route('/logout')
@authentication_required
def logout():
    if "id" in session:
        id_session = session["id"]
        session.pop('id', None)
        get_db().delete_session(id_session)
    return redirect('/')


@app.errorhandler(404)
def page_inexistante(e):
    return render_template('404.html'), 404


@app.errorhandler(FormInputError)
def erreur_formulaire(e):
    return render_template(e.template,
                           article=e.article,
                           erreur=e.message,
                           ), e.code


app.secret_key = "(*&*&322387he738220)(*(*18352086"