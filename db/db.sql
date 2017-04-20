create table article (
  id integer primary key,
  titre varchar(100),
  identifiant varchar(50),
  auteur varchar(100),
  date_publication text,
  paragraphe varchar(500)
);

create table session (
  id integer primary key,
  id_session varchar(32),
  username varchar(25)
);

create table user (
  id integer primary key,
  username varchar(25) unique,
  email varchar(100),
  salt varchar(32),
  hash varchar(128)
);

create table jeton_mdp (
  id integer primary key,
  username varchar(25),
  jeton varchar(32),
  time_jeton text
);

create table jeton_invitation (
  id integer primary key,
  email varchar(25),
  jeton varchar(32),
  time_jeton text
);

insert into user values (null, 'correcteur', "correcteur@gmail.com", "4a5a0081b82840f4913e78776c9f18c4", 'df837e2f2abbc4e8afc52adc96ee0c9f794c594da8b4016e377fc56e4794180393d9d77a0b9e9fcad7abc9936b178e502c289c26c50b7b9b9ae9b27d3bf46d86');