import os
import requests

from flask import Flask, session
from flask import render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Configure session to use filesystem
### Change path to your postgres database below ###
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['SQLALCHEMY_DATABASE_URI']
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

Session(app)

username = None

### Change your secret key below ###
app.secret_key = os.getenv("SECRET_KEY")

# Set up database
engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
db = scoped_session(sessionmaker(bind=engine))

# Homepage
@app.route("/")
def index():
    check_session()
    return render_template("index.html")

# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if check_if_logged_in():     
        return redirect(url_for("index"))
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Information about current page to render on complete page
        page = "login"
        registered_user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
        if registered_user and check_password_hash(registered_user.password, password):
            session["username"] = username
            return render_template("complete.html", page=page, message="Login successful")
        else:
            return render_template("complete.html", page=page, message="Login unsuccessful")

# Register page
@app.route("/register", methods=["GET", "POST"])
def register():
    if check_if_logged_in():     
        return redirect(url_for("index"))
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Information about current page to render on complete page
        page = "register"
        existing_user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
        # Register and log in user if username is not taken
        if existing_user is None:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username": username, "password": generate_password_hash(password, method="sha256")})
            db.commit()
            session["username"] = username
            return render_template("complete.html", page=page, message="Registration completed successfully")
        else:
            return render_template("complete.html", page=page, message="This username is already taken")

# Search page
@app.route("/search", methods=["GET", "POST"])
def search():
    if not check_if_logged_in():     
        return redirect(url_for("index"))
    if request.method == "GET":
        return render_template("search.html")
    # Search for books that fit the pattern (case insensitive)
    elif request.method == "POST":
        search = "%{}%".format(request.form.get("search"))
        books = db.execute("SELECT * FROM books WHERE (LOWER(isbn) LIKE LOWER(:search)) OR (LOWER(title) LIKE LOWER(:search)) OR (LOWER(author) LIKE LOWER(:search))", {"search": search}).fetchall()
        return render_template("search.html", books=books)

# Book page (uses book_id from the database)
@app.route("/books/<int:book_id>", methods=["GET", "POST"])
def books(book_id):
    if not check_if_logged_in():     
        return redirect(url_for("index"))
    # Make sure book exists
    user_id = db.execute("SELECT user_id FROM users WHERE (username = :username)", {"username": session["username"]}).fetchone()[0]
    book = db.execute("SELECT * FROM books WHERE book_id = :book_id", {"book_id": book_id}).fetchone()
    if book is None:
        return render_template("error.html", message="404 Book not found"), 404
    if request.method == "POST":
        # Adding or changing the review
        if "add" in request.form or "update" in request.form :
            review = request.form.get("review")
            rating = int(request.form.get("rating"))
            if (rating < 1 & rating > 5):
                return render_template("error.html", message="Denied"), 404
            # Check if user already posted a review for the book
            db_review = db.execute("SELECT * FROM reviews WHERE (book_id = :book_id AND user_id = :user_id)", {"book_id": book_id, "user_id": user_id}).fetchone()
            if db_review is None:
                db.execute("INSERT INTO reviews (user_id, book_id, review_text, review_score) VALUES (:user_id, :book_id, :review_text, :review_score)", {"user_id": user_id, "book_id": book_id, "review_text": review, "review_score": rating})
                db.commit()
            else:
                db.execute("UPDATE reviews SET review_text = :review_text, review_score = :review_score WHERE review_id = :review_id", {"review_text": review, "review_score": rating, "review_id": db_review.review_id})
                db.commit()
        # Deleting the review
        elif "delete" in request.form:
            db.execute("DELETE FROM reviews WHERE (book_id = :book_id AND user_id = :user_id)", {"book_id": book_id, "user_id": user_id})
            db.commit()
    # Get the existing reviews and separate the one written by the user
    db_reviews = db.execute("SELECT reviews.review_text, reviews.review_score, users.username FROM reviews INNER JOIN users ON reviews.user_id=users.user_id WHERE (reviews.book_id = :book_id AND NOT reviews.user_id = :user_id)", {"book_id": book_id, "user_id": user_id}).fetchall()
    user_review = db.execute("SELECT * FROM reviews WHERE (book_id = :book_id AND user_id = :user_id)", {"book_id": book_id, "user_id": user_id}).fetchone()
    # Get data from Goodreads API
    ### Change key to your goodreads API key below ###
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": os.getenv("GOODREADS_API_KEY"), "isbns": book.isbn})
    if res.status_code == 200:
        goodreadsData = res.json()
        return render_template("books.html", book=book, goodreadsData=goodreadsData, db_reviews=db_reviews, user_review=user_review)
    return render_template("books.html", book=book, db_reviews=db_reviews, user_review=user_review)

# API page
@app.route("/api/<string:isbn>")
def api(isbn):
    # Make sure isbn exists
    book = db.execute("SELECT * FROM books WHERE (isbn = :isbn)", {"isbn": isbn}).fetchone()
    if book is None:
        return render_template("error.html", message="404 Book not found"), 404
    review = db.execute("SELECT COUNT(reviews), AVG(reviews.review_score) FROM reviews WHERE (book_id = :book_id)", {"book_id": book.book_id}).fetchone()
    try:
        avg_score = float(round(review[1], 2))
    except:
        avg_score = float(round(1, 2))
    json = {
            "title": book.title, 
            "author": book.author,
            "year": book.year,
            "isbn": book.isbn,
            "review_count": review[0],
            "average_score": avg_score,
        }
    return render_template("api.html", json=json)

# Logout page
@app.route("/logout")
def logout():
    session["username"] = None
    return redirect(url_for("index"))

# Checks if session variable exists and creates it if does not
def check_session():
    try:
        session["username"]
    except:
        session["username"] = None

# Checks if user is logged in
def check_if_logged_in():
    check_session()
    if session["username"] is not None:
        return True
    return False

# Main method
if __name__ == "__main__":
    app.run()
