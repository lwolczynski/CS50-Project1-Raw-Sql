import os
import requests

from flask import Flask, session
from flask import render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from sqlalchemy import and_, or_
from models import *
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# Configure session to use filesystem
### Change path to your postgres database below ###
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

### Change your secret key below ###
app.secret_key = os.getenv("SECRET_KEY")

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Set up database
db.init_app(app)

# Homepage
@app.route("/")
def index():
    return render_template("index.html")

# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Information about current page to render on complete page
        page = "login"
        registered_user = User.query.filter_by(username = username).first()
        if registered_user and registered_user.check_password(password):
            login_user(registered_user)
            return render_template("complete.html", page=page, message="Login successful")
        else:
            return render_template("complete.html", page=page, message="Login unsuccessful")

# Register page
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Information about current page to render on complete page
        page = "register"
        existing_user = User.query.filter_by(username=username).first()
        # Register and log in user if username is not taken
        if existing_user is None:
            user = User(username=username, password=generate_password_hash(password, method="sha256"))
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return render_template("complete.html", page=page, message="Registration completed successfully")
        else:
            return render_template("complete.html", page=page, message="This username is already taken")

# Search page
@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "GET":
        return render_template("search.html")
    # Search for books that fit the pattern (case insensitive)
    elif request.method == "POST":
        search = "%{}%".format(request.form.get("search"))
        books = Book.query.filter(Book.isbn.ilike(search) | Book.title.ilike(search) | Book.author.ilike(search)).all()
        return render_template("search.html", books=books)

# Book page (uses book_id from the database)
@app.route("/books/<int:book_id>", methods=["GET", "POST"])
@login_required 
def books(book_id):
    # Make sure book exists
    book = Book.query.get(book_id)
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
            db_review = Review.query.filter(and_(Review.book_id==book_id, Review.user_id==current_user.get_id())).first()
            if db_review is None:
                new_review = Review(user_id=current_user.get_id(), book_id=book_id, review_text=review, review_score=rating)   
                db.session.add(new_review)
            else:
                db_review.review_text = review
                db_review.review_score = rating
            db.session.commit()
        # Deleting the review
        elif "delete" in request.form:
            db_review = Review.query.filter(and_(Review.book_id==book_id, Review.user_id==current_user.get_id())).first()
            db.session.delete(db_review)
            db.session.commit()
    # Get the existing reviews and separate the one written by the user
    db_reviews = Review.query.filter(Review.book_id==book_id).all()
    user_review = [review for review in db_reviews if review.user_id == current_user.user_id]
    if user_review:
        user_review=user_review[0]
        db_reviews.remove(user_review)
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
    book = Book.query.filter_by(isbn=isbn).first()
    if book is None:
        return render_template("error.html", message="404 Book not found"), 404
    return render_template("api.html", book=book)

# Logout page
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

# Load user data 
@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(user_id=id).first()

# Redirects to homepage if user is not logged in
@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for("index"))

# Main method
if __name__ == "__main__":
    app.run()