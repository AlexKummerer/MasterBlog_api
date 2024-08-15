# models.py
import uuid
import json
import os
from datetime import UTC, datetime

POSTS_FILE = "posts.json"


class User:
    def __init__(self, username, password, bcrypt):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password, bcrypt):
        return bcrypt.check_password_hash(self.password, password)


class Comment:
    def __init__(self, id, post_id, content):
        self.id = id
        self.post_id = post_id
        self.content = content

    def to_dict(self):
        return {"id": self.id, "post_id": self.post_id, "content": self.content}


class Category:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Tag:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class PostNotFoundException(Exception):
    pass


class InvalidDataException(Exception):
    pass


class Post:
    def __init__(
        self,
        id,
        title,
        content,
        author,
        date=None,
        comments=None,
        categories=None,
        tags=None,
    ):
        self.id = id
        self.title = title
        self.content = content
        self.author = author
        self.date = date if date else datetime.now(UTC).isoformat()
        self.comments = comments if comments is not None else []
        self.categories = categories if categories is not None else []
        self.tags = tags if tags is not None else []

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "author": self.author,
            "date": self.date,
            "comments": [comment.to_dict() for comment in self.comments],
            "categories": [category.to_dict() for category in self.categories],
            "tags": [tag.to_dict() for tag in self.tags],
        }

    def add_comment(self, content):
        new_comment = Comment(uuid.uuid4().hex, self.id, content)
        self.comments.append(new_comment)
        return new_comment

    def add_category(self, name):
        new_category = Category(uuid.uuid4().hex, name)
        self.categories.append(new_category)
        return new_category

    def add_tag(self, name):
        new_tag = Tag(uuid.uuid4().hex, name)
        self.tags.append(new_tag)
        return new_tag


class PostList:
    def __init__(self, file_path=POSTS_FILE):
        self.file_path = file_path
        self.posts = self.load_posts()

    def load_posts(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as file:
                    posts_data = json.load(file)
                    return [Post(**post_data) for post_data in posts_data]
            except (IOError, json.JSONDecodeError):
                return []
        return []

    def save_posts(self):
        with open(self.file_path, "w") as file:
            json.dump([post.to_dict() for post in self.posts], file, indent=4)

    def get_all(self):
        return [post.to_dict() for post in self.posts]

    def add_post(self, title, content, author, categories=None, tags=None):
        new_id = uuid.uuid4().hex
        new_post = Post(
            new_id, title, content, author, categories=categories, tags=tags
        )
        self.posts.append(new_post)
        self.save_posts()
        return new_post

    def find_post_by_id(self, post_id):
        return next((post for post in self.posts if post.id == post_id), None)

    def delete_post(self, post_id):
        post = self.find_post_by_id(post_id)
        if post:
            self.posts = [post for post in self.posts if post.id != post_id]
            self.save_posts()
            return post
        raise PostNotFoundException(f"Post with ID {post_id} not found")

    def update_post(self, post_id, title, content, author):
        post = self.find_post_by_id(post_id)
        if post:
            post.title = title
            post.content = content
            post.author = author
            post.date = datetime.utcnow().isoformat()  # Update the date when editing
            self.save_posts()
            return post
        raise PostNotFoundException(f"Post with ID {post_id} not found")

    def sort_posts(self, sort_by=None, direction="asc"):
        if sort_by:
            if sort_by not in ["title", "content", "author", "date"]:
                raise InvalidDataException("Invalid sort_by parameter")
            if direction not in ["asc", "desc"]:
                raise InvalidDataException("Invalid direction parameter")
            return sorted(
                self.posts,
                key=lambda post: getattr(post, sort_by),
                reverse=direction == "desc",
            )
        return self.posts

    @staticmethod
    def validate_post_data(data):
        if (
            not data
            or "title" not in data
            or "content" not in data
            or "author" not in data
            or not data["title"]
            or not data["content"]
            or not data["author"]
        ):
            raise InvalidDataException("Missing title, content, or author")
