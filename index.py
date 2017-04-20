# coding=utf-8

from flask import Flask, render_template, g, request, redirect, abort, session, jsonify
from database import Database
from authentification import authentication_required, is_authenticated
from gmail import envoyer_courriel, envoyer_invitation
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
    if is_authenticated(session):
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
def admin():
    if is_authenticated(session):
        articles = get_db().get_all_articles()
        return render_template('admin.html',
                               articles=articles)
    else:
        return redirect('/login_form')


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
    valider_unique(article, 'admin_nouveau.html', get_db())

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
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    try:
        user = get_db().get_user_infos(request.form['username'])
        hashed_password = hashlib.sha512(request.form['password'] + user[0]).hexdigest()

        if hashed_password == user[1]:
            id_session = uuid.uuid4().hex
            get_db().save_session(id_session, request.form['username'])
            session['id'] = id_session
            return redirect('/admin')
        else:
            raise Exception
    except:
        raise FormInputError('login.html',
                             None,
                             "Nom d'usager ou mot de passe incorrect.",
                             401)


@app.route('/logout')
@authentication_required
def logout():
    if "id" in session:
        id_session = session["id"]
        session.pop('id', None)
        get_db().delete_session(id_session)
    return redirect('/')


@app.route('/recuperation')
def recuperation():
    return render_template('recuperation.html')


@app.route('/recuperation_form', methods=['POST'])
def recuperation_form():
    try:
        envoyer_courriel(request.form['username'], get_db())
        return redirect('/login_form')
    except:
        raise FormInputError('recuperation.html',
                             None,
                             "Nom d'usager inexistant.",
                             401)


@app.route('/nouveau_mdp', methods=['GET'])
def nouveau_mdp():
    return render_template('nouveau_mdp.html',
                           jeton=request.args['jeton'])


@app.route('/nouveau_mdp_form', methods=['POST'])
def nouveau_mdp_form():
    username = request.form['username']
    jeton = get_db().get_jeton_mdp(username)
    if jeton[0] == request.form['jeton'] and jeton[1] > datetime.datetime.now().isoformat():
        try:
            user = get_db().get_user_infos(username)
            hashed_password = hashlib.sha512(request.form['password'] + user[0]).hexdigest()
            get_db().modifier_mdp(username, hashed_password)
            get_db().delete_jeton_mdp(username)
            return redirect('/login_form')
        except:
            raise FormInputError('nouveau_mdp.html',
                                 None,
                                 "Nom d'usager inexistant.",
                                 401)
    else:
        get_db().delete_jeton_mdp(username)
        raise FormInputError('recuperation_form.html',
                             None,
                             u"La limite de temps est expirée, veuillez recommencer",
                             401)


@app.route('/invitation')
def invitation():
    return render_template('invitation.html')


@app.route('/invitation_form', methods=['POST'])
def invitation_form():
    envoyer_invitation(request.form['email'], get_db())
    return redirect('/confirmation')


@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')


@app.route('/creer_compte', methods=['GET'])
def creer_compte():
    jeton = get_db().get_jeton_invitation(request.args['email'])
    if jeton[0] == request.args['jeton'] and jeton[1] > datetime.datetime.now().isoformat():
        return render_template('creer_compte.html',
                               jeton=request.args['jeton'],
                               email=request.args['email'])
    else:
        get_db().delete_jeton_invitation(request.form['email'])
        raise FormInputError('creer_compte.html',
                             None,
                             u"La limite de temps est expirée, veuillez contacter un administrateur.",
                             401)


@app.route('/creer_compte_form', methods=['POST'])
def creer_compte_form():
    try:
        salt = uuid.uuid4().hex
        hashed_password = hashlib.sha512(request.form['password'] + salt).hexdigest()
        get_db().create_user(request.form['username'], request.form['email'], salt, hashed_password)
        get_db().delete_jeton_invitation(request.form['email'])
        return redirect('/login_form')
    except:
        raise FormInputError('creer_compte.html',
                             None,
                             u"Ce nom d'utilisateur existe déjà.",
                             401)


@app.route('/suggest_id/<identifiant>', methods=['GET'])
def suggest_id(identifiant):
    serial = 0
    nouvel_id = identifiant

    while True:
        try:
            get_db().get_article(nouvel_id)
            nouvel_id = identifiant + str(serial)
            serial += 1
        except:
            return nouvel_id


@app.route('/check_id/<identifiant>', methods=['GET'])
def check_id(identifiant):
    try:
        get_db().get_article(identifiant)
        return "false"
    except:
        return "true"


@app.route('/api/creer_article', methods=['POST'])
def creer_article():
    article = article_from_form(request.args)

    try:
        get_db().get_article(article.identifiant)
        return "", 400
    except:
        get_db().nouveau(article)
        data = {"auteur": article.auteur,
                "titre": article.titre,
                "identifiant": article.identifiant,
                "date_publication": article.date,
                "paragraphe": article.paragraphe}
        return jsonify(data)


@app.route('/api/articles', methods=['GET'])
def articles():
    articles = get_db().get_all_articles()

    data = {"articles": [{"titre": each.titre,
             "auteur": each.auteur,
             "url": "localhost:5000/article/" + each.identifiant}
            for each in articles]}
    return jsonify(data)


@app.route('/api/articles/<identifiant>', methods=['GET'])
def infos_article(identifiant):
    try:
        article = get_db().get_article(identifiant)
        data = {"auteur": article.auteur,
                "titre": article.titre,
                "identifiant": article.identifiant,
                "date_publication": article.date,
                "paragraphe": article.paragraphe}
        return jsonify(data)
    except:
        return "", 400


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
