from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///auth_prac"
app.app_context().push()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.confdgfvadzxvadfvzig["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)


@app.route("/")
def redirect_register():
    return redirect("/register")


@app.route("/register")
def register_form():
    form = UserForm()
    return render_template("register.html", form=form)


@app.route("/register", methods=["POST"])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash(
                "Username already exists. Please choose a different username", "danger"
            )
            return redirect("/register")

        password = form.password.data
        email = form.email.data
        existing_email = User.query.filter_by(email=email).first()

        if existing_email:
            flash(
                "Email already exists. Please choose a different Email or login",
                "danger",
            )
            return redirect("/register")

        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        db.session.commit()
        session["username"] = new_user.username
        flash("Welcome!, You have register successfully!!", "primary")
        return redirect(f"/users/{new_user.username}")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, "danger")

    return render_template("register.html", form=form)


@app.route("/login")
def login_form():
    form = LoginForm()
    return render_template("login.html", form=form)


@app.route("/login", methods=["POST"])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!", "success")
            session["username"] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Invalid username/password"]

    return render_template("login.html", form=form)


@app.route("/secret")
def show_secret():
    return "You made it!"


@app.route("/logout")
def logout_user():
    session.pop("username")
    flash("Goodbye!", "info")
    return redirect("/")


@app.route("/users/<username>")
def show_info(username):
    user = User.query.get_or_404(username)
    feedbacks = Feedback.query.filter(Feedback.username == user.username).all()
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect("/login")
    else:
        return render_template("user_info.html", user=user, feedbacks=feedbacks)


@app.route("/feedback/<username>/add", methods=["GET", "POST"])
def show_feedback(username):
    user = User.query.get_or_404(username)
    if "username" not in session:
        flash("Please log in first", "danger")
        return redirect("/login")

    form = FeedbackForm()

    all_feedback = Feedback.query.all()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_feedback = Feedback(
            title=title, content=content, username=session["username"]
        )
        db.session.add(new_feedback)
        db.session.commit()
        flash("Feedback Added!", "succes")
        return redirect(f"/users/{user.username}")

    return render_template("feedbackform.html", form=form, user=user)


@app.route("/feedback/<username>/edit/<int:id>", methods=["GET", "POST"])
def edit_feedback(username, id):
    # if "username" not in session:
    #     flash("Please log in first", "danger")
    #     return redirect("/login")
    feedback = Feedback.query.get_or_404(id)
    if username != session["username"]:
        flash("improper user", "danger")
        return redirect(f"/users/{session['username']}")

    user = User.query.get_or_404(username)
    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.add(feedback)
        db.session.commit()
        flash("Feedback Updated")
        return redirect(f"/users/{user.username}")
    else:
        return render_template(
            "edit_feedbackform.html", form=form, user=user, feedback=feedback
        )


@app.route("/feedback/<username>/delete/<id>", methods=["POST"])
def delete_post(username, id):
    feedback = Feedback.query.get_or_404(id)
    user = User.query.get_or_404(username)

    if "username" not in session:
        flash("Please log in first!", "danger")
        return redirect("/login")

    if feedback.username == session["username"]:
        db.session.delete(feedback)
        db.session.commit()
        flash("Feedback Delated!", "info")
        return redirect(f"/users/{user.username}")

    flash("You do not have permission to do that", "danger")
    return redirect("/")


@app.route("/feedback/<username>/delete_user", methods=["POST"])
def delete_user(username):
    feedbacks = Feedback.query.filter_by(username=username).all()
    user = User.query.get_or_404(username)

    for feedback in feedbacks:
        db.session.delete(feedback)

    db.session.delete(user)
    logout_user()
    db.session.commit()

    flash("User and associated feedbacks have been delated!", "info")
    return redirect("/")
