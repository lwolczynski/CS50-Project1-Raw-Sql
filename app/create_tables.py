# Creates postgres db tables

from app import app, db

with app.app_context():
    db.execute("CREATE TABLE users (user_id serial primary key, username varchar(40) NOT NULL UNIQUE, password varchar(80) NOT NULL)")
    db.execute("CREATE TABLE books (book_id serial primary key, isbn varchar(10) NOT NULL UNIQUE, title varchar(255) NOT NULL, author varchar(255) NOT NULL, year integer NOT NULL)")
    db.execute("CREATE TABLE reviews (review_id serial primary key, user_id integer NOT NULL, book_id integer NOT NULL, review_text character varying(1000) NOT NULL, review_score smallint NOT NULL, FOREIGN KEY (user_id) REFERENCES users(user_id), FOREIGN KEY (book_id) REFERENCES books(book_id))")   
    db.commit()