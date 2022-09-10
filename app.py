"""Blogly application."""


from itertools import combinations_with_replacement
from flask import Flask, render_template, request, redirect
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User

#Required for flask
app = Flask(__name__) 

#For Flask Debug Toolbar
app.config ['SECRET_KEY'] = "oh-so-Secret"
debug = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False #Should intercept redirects


#Required for Sql alchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #Makes the SQl MOdification trak warnign go away
app.config['SQLALCHEMY_ECHO'] = True #Prints all SQL statements to the terminal (helps in debuggin)


# Calls the connect_db def from models.py and creates all the table
connect_db(app)
db.create_all()

@app.route('/')
def root():
    """Redirect to list of users."""

    return redirect("/users")


@app.route("/users")
def user_list():
    """HOme page"""
    users = User.query.order_by(User.last_name, User.first_name).all()
    return  render_template ("users.html", users=users)

@app.route("/users/<int:user_id>")
def user_info(user_id):
    user = User.query.get_or_404(user_id)
    return render_template ("userinfo.html", u = user)

@app.route ("/users/addUser", methods=["GET"])
def display_form():
    return render_template ("displayform.html")

@app.route ("/users/addUser", methods = ["POST"])
def add_new_user():
    """Get the inputs from form and add the info to the database"""
    new_user = User(
                    first_name = request.form ['fname'],
            last_name   = request.form['lname'],
            image_url   = request.form['url'] or None )
    db.session.add(new_user)
    db.session.commit()
    
    return redirect("/users")

@app.route ("/users/<int:user_id>/edit")
def edit_user(user_id):
    """Get the user info through the user id and display the user edit form"""
    user = User.query.get_or_404(user_id)
    return render_template("edituserform.html", user=user)

@app.route ("/users/<int:user_id>/edit", methods =["POST"])
def update_user(user_id):
    """Get the updated user info and update it in the database"""
    user = User.query.get_or_404(user_id)
    if (request.form.get('fname')):
        user.first_name =request.form.get('fname')
    if (request.form.get('lname')):
        user.last_name =request.form.get('lname')
    if (request.form.get('url')):
        user.image_url =request.form.get('url')

    print (user.full_name)

    db.session.add(user)
    db.session.commit()

    return redirect ("/users")

@app.route ("/users/<int:user_id>/delete", methods = ["POST"])
def delete_user(user_id):
    """Get the user detail through user id, delete the user and commit the changes"""
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return redirect("/users")



