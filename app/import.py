# Imports data from csv to postgres db

import csv

from app import app, db

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        if year == "year":
            continue
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added book with ISBN {isbn}")
    db.commit()

if __name__ == "__main__":
    with app.app_context():
        main()