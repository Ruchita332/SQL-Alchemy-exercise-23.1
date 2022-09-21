"""Models for Blogly."""
import datetime
from email.policy import default
from enum import unique
from tkinter import CASCADE
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



DEFAULT_IMAGE_URL = "https://www.freeiconspng.com/uploads/icon-user-blue-symbol-people-person-generic--public-domain--21.png"



# User model for SQLAlchemy with following columns:

# id, an autoincrementing integer number that is the primary key
# first_name and last_name
# image_url for profile images

class User (db.Model): # * All model should have subclass db.Model
    """User"""
    __tablename__ = "users" # *Specifying the table name with __tablename__

    def __repr__(self):
        """Show info about user"""
        # for better representation
        u = self;
        return f"<User {u.id} {u.first_name} {u.last_name} >"


    id = db.Column (db.Integer, 
                    primary_key = True,
                    autoincrement = True)
    first_name = db.Column (db.String (50), 
                            nullable = False)
    last_name = db.Column (db.String (50), 
                            nullable = False)
    image_url = db.Column (db.Text, nullable = False, default = DEFAULT_IMAGE_URL)
    
    posts = db.relationship ('Post', backref = 'user', cascade="all, delete-orphan")


    @property # Q what is the purpose of @ property decorator
    def full_name(self):
        """Return full name of user."""

        return f"{self.first_name} {self.last_name}"

class Post(db.Model):
    """"Post by User"""

    __tablename__ = "posts"

    id = db.Column (db.Integer, primary_key = True)
    title = db.Column (db.Text, nullable = False, default = "Untitled")
    content = db.Column (db.Text, nullable = False)
    created_at = db.Column (db.DateTime, nullable = False, default = datetime.datetime.now)
    user_id = db.Column (db.Integer, db.ForeignKey ('users.id'), nullable = False)

    def __repr__(self):
        """Show info about post"""
        return f"<Post {self.id} {self.content} {self.created_at} >"

    @property
    def friendly_date(self):
        """Return nicely-formatted date."""

        return self.created_at.strftime("%a %b %-d  %Y, %-I:%M %p")


class PostTag(db.Model):
    """M2m relation between post and tag table"""
    __tablename__ = "posts_tags"
        
    post_id = db.Column (db.Integer, db.ForeignKey ('posts.id'), primary_key=True)
    tag_id = db.Column (db.Integer, db.ForeignKey ('tags.id'), primary_key=True)

    def __repr__(self):
        """Show info about post_tag"""
        return f"<PostTag {self.post_id} {self.tag_id} >"

class Tag(db.Model):
    """Tagging for posts by user"""

    __tablename__ ="tags"

    def __repr__(self):
        """Show info about Tag"""
        return f"<Tag {self.id} {self.name}>"


    id = db.Column (db.Integer, primary_key= True)
    name = db.Column (db.Text, nullable = False, unique= True)

    posts = db.relationship ('Post', secondary = "posts_tags", backref = "tags")





def connect_db(app):
    """for flask app """
    db.app = app
    db.init_app(app)