# CS50 Project 1
**Web Programming with Python and JavaScript**

This is a simple book review website written in Python and using Flask framework and SQLAlchemy library.
It is based on CS50x exercise requirements, but does not follow them fully (used slightly different libraries than required). The original project description is included in repository (file Project1_Books.html).

## Repository files
- app.py: the main file; execute to run the project
- books.csv: file containing 5000 books details
- create_tables.py: script that creates required tables in database
- import.py: script that imports books.csv to database
- models.py: file describing database models
- /templates: webpage templates to render
- /static: static files (one file to be precise: styles.css) that are referenced when webpages are rendered

## How to run?
Run create_tables.py to prepare your database and import.py if you want to import books.csv to your database.\
Before you run app.py set your environmental variables (postgres database path, secret key and goodreads API key) — see .env file.

## Demo
This project has been deployed on Heroku. You can see in deployed [here](/).