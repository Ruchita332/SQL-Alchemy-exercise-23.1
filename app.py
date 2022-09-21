"""Blogly application."""


from itertools import combinations_with_replacement
from operator import methodcaller
from turtle import pos, title
from flask import Flask, render_template, request, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag

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
    return  render_template ("users/users.html", users=users)

@app.route("/users/<int:user_id>")
def user_info(user_id):
    user = User.query.get_or_404(user_id)
    return render_template ("users/userinfo.html", u = user)

@app.route ("/users/addUser", methods=["GET"])
def display_form():
    return render_template ("users/displayform.html")

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
    return render_template("users/edituserform.html", user=user)

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
    tags = Tag.query.all()

    return render_template ("posts/addpostform.html", user = user, tags=tags)

@app.route ("/users/<int:user_id>/posts/new", methods = ["POST"])
def add_new_post (user_id):
    """Get the posts data and add it to the database"""
    user = User.query.get_or_404(user_id)
    tag_ids = [int(num) for num in request.form.getlist ("tags")]
    tags = Tag.query.filter (Tag.id.in_(tag_ids)).all()
    new_post = Post(title= request.form["title"],
                        content = request.form["content"],
                        user = user,
                        tags=tags)

    db.session.add(new_post)
    db.session.commit()

    flash (f"Post '{new_post.title}' added.")
    # return tag_ids;
    return redirect (f"/users/{user_id}")

@app.route ("/posts/<int:post_id>")
def display_posts(post_id):
    """Get the post detail through post_id and display it"""
    post = Post.query.get_or_404(post_id)
    # return post.user.full_name
    return render_template ("posts/post.html", post = post)

@app.route ("/posts/<int:post_id>/edit")
def display_post_edit_form(post_id):
    """Get the post info and display the edit form"""
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    return render_template ('posts/postedit.html', post = post, tags=tags)

@app.route ("/posts/<int:post_id>/edit", methods =["POST"])
def edit_post(post_id):
    """Get the edited details submitted though the edit form update it in the database"""
    post = Post.query.get_or_404(post_id)

    if (request.form.get('title')):
        post.title =request.form.get('title')
    if (request.form.get('content')):
        post.content =request.form.get('content')
    tag_ids = [int(num) for num in request.form.getlist("tags")]
    post.tags = Tag.query.filter (Tag.id.in_(tag_ids)).all()
    
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


###############################################################
#Part Three: M2M relationship




# GET /tags
@app.route ("/tags")
def display_tag_list():
    """Lists all tags, with links to the tag detail page."""
    tags = Tag.query.all()
    return render_template("/tags/dispalyTagList.html", tags=tags)
# GET /tags/[tag-id]

@app.route ("/tags/new")
def add_new_tag_form():
    """Shows a form to add a new tag"""
    posts = Post.query.all()
    return render_template("tags/formNewTag.html", posts =posts)

# POST /tags/new
@app.route ("/tags/new", methods =["POST"])
def add_new_tag():
    """Process add form, adds tag, and redirect to tag list"""

    post_ids = [int(num) for num in request.form.getlist("posts")]
    posts = Post.query.filter(Post.id.in_(post_ids)).all()

    new_tag = Tag (name = request.form["name"], posts= posts);
    
    db.session.add(new_tag);
    db.session.commit();

    flash (f"'{new_tag.name}' added.")

    return redirect("/tags")

@app.route ("/tags/<int:tag_id>")
def display_post_under_tag(tag_id):
    """Display all the post under the same tag_id"""
    # Show detail about a tag. Have links to edit form and to delete.
    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()
    return render_template ("/tags/tag_posts.html", tag=tag, posts=posts)

@app.route ("/tags/<int:tag_id>/edit")
def display_tag_edit_form(tag_id):
    """# Show edit form for a tag"""
    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()
    return render_template("/tags/edit.html", tag= tag, posts = posts)

@app.route ("/tags/<int:tag_id>/edit", methods =["POST"])
def display_tag_edit(tag_id):
    """# POST /tags/[tag-id]/edit"""
    # Process edit form, edit tag, and redirects to the tags list.

    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form['name']
    post_ids = [int(num) for num in request.form.getlist("posts")]
    tag.posts = Post.query.filter (Post.id.in_(post_ids)).all()

    db.session.add (tag)
    db.session.commit()

    flash (f"Tag '{tag.name}' edited.")

    return redirect(f"/tags")

@app.route ("/tags/<int:tag_id>/delete", methods =["POST"])
def delete_tag(tag_id):
    """# POST /tags/[tag-id]/delete # Delete a tag."""
    tag = Tag.query.get_or_404(tag_id)

    db.session.delete(tag)
    db.session.commit()

    flash (f"Tag '{tag.name}' deleted.")


    return redirect("/tags")
