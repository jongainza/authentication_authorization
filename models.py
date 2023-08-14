from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, db.ForeignKey("users.username"))

    user = db.relationship("User", backref="feedback")


class User(db.Model):
    __tablename__ = "users"

    username = db.Column(db.String(20), nullable=False, primary_key=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    @classmethod
    def register(cls, username, psw, email, first, last):
        """register user w/hashed password & reeturn user."""

        hashed = bcrypt.generate_password_hash(psw)
        # turn bytestring into normal unicode (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(
            username=username,
            password=hashed_utf8,
            email=email,
            first_name=first,
            last_name=last,
        )

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate the user exists and password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # Return user instance
            return u
        else:
            return False
