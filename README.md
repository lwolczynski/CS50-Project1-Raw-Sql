# CS50 Project 1
**Web Programming with Python and JavaScript**

This is a simple book review website written in Python and using Flask framework and SQLAlchemy library.
It is based on CS50x exercise requirements. The original project description is included in repository (file Project1_Books.html).

## Repository files
- app.py: the main file; execute to run the project
- books.csv: file containing 5000 books details
- create_tables.py: script that creates required tables in database
- import.py: script that imports books.csv to database
- /templates: webpage templates to render
- /static: static files (one file to be precise: styles.css) that are referenced when webpages are rendered

## Database
There is no models file that would describe database structure, as one of requirements was to use raw SQL commands.\
After running create_tables.py database tables should look like this:
#### users
| user_id      | Username     | Password     |
| ------------ | ------------ | ------------ |
| [PK] integer | varchar (40) | varchar (80) |
#### books
| book_id      | isbn         | title         | author        | year    |
| ------------ | ------------ | ------------- | ------------- | ------- |
| [PK] integer | varchar (10) | varchar (255) | varchar (255) | integer |
#### reviews
| review_id    | user_id      | book_id      | review_text    | review_score |
| ------------ | ------------ | ------------ | -------------- | ------------ |
| [PK] integer | [FK] integer | [FK] integer | varchar (1000) | smallint     |

## How to run?
Run create_tables.py to prepare your database and import.py if you want to import books.csv to your database.\
Before you run app.py set your environmental variables (postgres database path, secret key and goodreads API key) — see .env file.

## Demo
This project has been deployed on Heroku. You can see in deployed [here](https://cs50-project1-raw-sql-lw.herokuapp.com/).