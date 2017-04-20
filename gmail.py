# coding: utf8

# Copyright 2017 Jacques Berger
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import smtplib
import ConfigParser
import uuid
from datetime import datetime, timedelta
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

PATH_TO_CONFIG = 'C:\INF3005\TP1\config.txt'


def envoyer_courriel(username, db):
    config_parser = ConfigParser.RawConfigParser()
    config_parser.read(PATH_TO_CONFIG)

    source_address = config_parser.get('infos_email', 'email')
    source_password = config_parser.get('infos_email', 'password')
    destination = db.get_email(username)
    jeton = creer_jeton_mdp(username, db)

    subject = "1337CMS Modification du mot de passe"

    html = "<a href='http://localhost:5000/nouveau_mdp?jeton=" + jeton + "'>Cliquez pour changer de mot de passe</a>"

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = source_address
    msg['To'] = destination

    msg.attach(MIMEText(html, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(source_address, source_password)
    text = msg.as_string()
    server.sendmail(source_address, destination, text)
    server.quit()
    return None


def creer_jeton_mdp(username, db):
    jeton = uuid.uuid4().hex
    time = (datetime.now() + timedelta(minutes=30)).isoformat()
    db.save_jeton_mdp(username, jeton, time)
    return jeton


def envoyer_invitation(destination, db):
    config_parser = ConfigParser.RawConfigParser()
    config_parser.read(PATH_TO_CONFIG)

    source_address = config_parser.get('infos_email', 'email')
    source_password = config_parser.get('infos_email', 'password')
    destination = destination
    jeton = creer_jeton_invitation(destination, db)

    subject = "1337CMS Invitation pour nouveau compte"

    html = "<a href='http://localhost:5000/creer_compte?jeton=" + jeton + "&email=" + destination + "'>Cliquez pour creer un compte sur 1337CMS</a>"

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = source_address
    msg['To'] = destination

    msg.attach(MIMEText(html, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(source_address, source_password)
    text = msg.as_string()
    server.sendmail(source_address, destination, text)
    server.quit()
    return None


def creer_jeton_invitation(email, db):
    jeton = uuid.uuid4().hex
    time = (datetime.now() + timedelta(minutes=30)).isoformat()
    db.save_jeton_invitation(email, jeton, time)
    return jeton
