# Imports data from csv to postgres db

import csv

from app import app, db
from models import Book

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        if year == "year":
            continue
        book = Book(isbn=isbn, title=title, author=author, year=year)
        db.session.add(book)
        print(f"Added book with ISBN {isbn}")
    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        main()