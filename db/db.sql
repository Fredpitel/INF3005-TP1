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
  username varchar(25),
  email varchar(100),
  salt varchar(32),
  hash varchar(128)
);

insert into user values (null, 'correcteur', "correcteur@gmail.com", "4a5a0081b82840f4913e78776c9f18c4", '47ed445dbc431742c5a22559e709a739c00aaf5d2e723458ae62d50e4df56eef799ac8df382d5dbb8bea941f1851c1dea77b339a707ca0ab111f720f98ab0c2a');