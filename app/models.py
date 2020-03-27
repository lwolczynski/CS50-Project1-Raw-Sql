from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash

db = SQLAlchemy()

class User(db.Model):
    # Model for user accounts

    __tablename__ = "accounts"

    user_id = db.Column(db.Integer,
                        primary_key=True)
    username = db.Column(db.String(40),
                        nullable=False,
                        unique=True)
    password = db.Column(db.String(80),
                         unique=False,
                         nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return self.user_id

class Book(db.Model):
    # Model for books

    __tablename__ = "books"

    book_id = db.Column(db.Integer,
                        primary_key=True)
    isbn = db.Column(db.String(10),
                     nullable=False,
                     unique=True)
    title = db.Column(db.String(255),
                      unique=False,
                      nullable=False)
    author = db.Column(db.String(255),
                       unique=False,
                       nullable=False)
    year = db.Column(db.Integer,
                     unique=False,
                     nullable=False)

    # Returns information about the book in JSON format
    def toJson(self):
        return {
            "title": self.title, 
            "author": self.author,
            "year": self.year,
            "isbn": self.isbn,
            "review_count": self.getReviewsCount(),
            "average_score": self.getReviewsAvg(),
        }
    
    def getReviewsCount(self):
        return len(Review.query.filter_by(book_id=self.book_id).all())

    # Get average review rating for the book (returns 0.0 if no reviews)
    def getReviewsAvg(self):
        reviews = Review.query.filter_by(book_id=self.book_id).with_entities(Review.review_score).all()
        reviews = [r for r, in reviews]
        if reviews:
            return sum(reviews) / len(reviews)
        else:
            return 0.0

class Review(db.Model):
    # Model for reviews

    __tablename__ = "reviews"

    review_id = db.Column(db.Integer,
                          primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey("accounts.user_id"),
                        nullable=False)
    book_id = db.Column(db.Integer,
                        db.ForeignKey("books.book_id"),
                        nullable=False)
    review_text = db.Column(db.String(1000),
                            nullable=False,
                            unique=False)
    review_score = db.Column(db.SmallInteger,
                             unique=False,
                             nullable=False)
    
    # Get name of user who wrote review
    def getUsername(self):
        return User.query.filter_by(user_id=self.user_id).first().username
