"""Blogly application."""


from itertools import combinations_with_replacement
from operator import methodcaller
from turtle import title
from flask import Flask, render_template, request, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post

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
    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all();

    return render_template("homepage.html", posts = posts)

# @app.errorhandler(404)
# def page_not_found(e):
#     """Show 404 NOT Found page"""

#     return render_template ('404.html'), 404


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

    flash (f"New user '{new_user.full_name}' added.")
    
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

    # print (user.full_name)

    db.session.add(user)
    db.session.commit()
    
    flash (f"User '{user.full_name}' edited.")


    return redirect ("/users")

@app.route ("/users/<int:user_id>/delete", methods = ["POST"])
def delete_user(user_id):
    """Get the user detail through user id, delete the user and commit the changes"""
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return redirect("/users")

#######################################################################
# Posts routes

@app.route ("/users/<int:user_id>/posts/new")
def add_new_post_form(user_id):
    """Get the user info and display the form"""
    user = User.query.get_or_404(user_id)

    return render_template ("addpostform.html", user = user)

@app.route ("/users/<int:user_id>/posts/new", methods = ["POST"])
def add_new_post (user_id):
    """Get the posts data and add it to the database"""
    user = User.query.get_or_404(user_id)
    new_post = Post(title= request.form["title"],
                        content = request.form["content"],
                        user = user)

    db.session.add(new_post)
    db.session.commit()

    flash (f"Post '{new_post.title}' added.")
    return redirect (f"/users/{user_id}")

@app.route ("/posts/<int:post_id>")
def display_posts(post_id):
    """Get the post detail through post_id and display it"""
    post = Post.query.get_or_404(post_id)
    # return post.user.full_name
    return render_template ("post.html", post = post)

@app.route ("/posts/<int:post_id>/edit")
def display_post_edit_form(post_id):
    """Get the post info and display the edit form"""
    post = Post.query.get_or_404(post_id)
    return render_template ('postedit.html', post = post)

@app.route ("/posts/<int:post_id>/edit", methods =["POST"])
def edit_post(post_id):
    """Get the edited details submitted though the edit form update it in the database"""
    post = Post.query.get_or_404(post_id)

    if (request.form.get('title')):
        post.title =request.form.get('title')
    if (request.form.get('content')):
        post.content =request.form.get('content')
    
    db.session.add(post)
    db.session.commit()

    flash(f"Post '{post.title} edited.")
    # return "did it"

    return redirect (f"/users/{post.user_id}")

@app.route ("/posts/<int:post_id>/delete", methods =["POST"])
def delete_post(post_id):
    """Get the post info and delete it in the database"""
    post = Post.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()
    return redirect (f"/users/{post.user_id}")



