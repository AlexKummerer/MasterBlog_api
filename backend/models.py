"""
This module contains the models for the blog application. 

Raises:
    PostNotFoundException: Raised when a post is not found.
    InvalidDataException: Raised when the data provided is invalid.

Returns:
    _type_: 
        User: A user object.
        Comment: A comment object.
        Category: A category object.
        Tag: A tag object.
        Post: A post object.
        PostList: A list of posts.
"""

from typing import List
import uuid
import json
import os
from datetime import UTC, datetime

POSTS_FILE = "posts.json"


class User:
    """
    A class to represent a user.
    """

    def __init__(self, username: str, password: str, bcrypt: str) -> None:
        """
        Constructor for the User class.

        Args:
            username (str):    The username of the user.
            password (str):   The password of the user.
            bcrypt (str):  The bcrypt password of the user.
        """
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def to_dict(self) -> dict:
        """
        Convert the user to a dictionary.

        Returns:
            dict: A dictionary representation of the user.
        """
        return {"username": self.username}

    def check_password(self, password: str, bcrypt: str) -> bool:
        """
        Check if the provided password matches the user's password.

        Args:
            password (str):  The password to check.
            bcrypt (str): The bcrypt password of the user.

        Returns:
            bool:  True if the password matches, False otherwise.
        """
        return bcrypt.check_password_hash(self.password, password)


class Comment:
    """
    A class to represent a comment.
    """

    def __init__(self, comment_id: str, post_id: str, content: str) -> None:
        """
        Constructor for the Comment class

        Args:
            id (str): id of the comment
            post_id (str): id of the post
            content (str): content of the comment
        """
        self.id: str = comment_id
        self.post_id: str = post_id
        self.content: str = content

    def to_dict(self) -> dict:
        """
        Convert the comment to a dictionary.

        Returns:
            dict: A dictionary representation of the comment.
        """
        return {"id": self.id, "post_id": self.post_id, "content": self.content}

    def __str__(self):
        return self.content


class Category:
    """
    A class to represent a category.
    """

    def __init__(self, category_id: str, name: str) -> None:
        """
        Constructor for the Category class

        Args:
            id (str): id of the category
            name (str): name of the category
        """
        self.id = category_id
        self.name = name

    def to_dict(self) -> dict:
        """
        Convert the category to a dictionary.

        Returns:
            dict: A dictionary representation of the category.
        """
        return {"id": self.id, "name": self.name}

    def __str__(self):
        return self.name


class Tag:
    """A class to represent a tag."""

    def __init__(self, tag_id: str, name: str) -> None:
        """
        Constructor for the Tag class

        Args:
            id (str):  id of the tag
            name (str): name of the tag
        """
        self.id = tag_id
        self.name = name

    def to_dict(self) -> dict:
        """Convert the tag to a dictionary.

        Returns:
            dict: A dictionary representation of the tag.
        """
        return {"id": self.id, "name": self.name}

    def __str__(self):
        return self.name


class PostNotFoundException(Exception):
    """Raised when a post is not found.

    Args:
        Exception (_type_): The base class for exceptions in Python.
    """


class InvalidDataException(Exception):
    """
    Raised when the data provided is invalid.

    Args:
        Exception (_type_): The base class for exceptions in Python.
    """


class Post:
    """A class to represent a blog post."""

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-arguments

    def __init__(
        self,
        post_id: str,
        title: str,
        content: str,
        author: str,
        date: str = None,
        comments: List[Comment] = None,
        categories: List[Category] = None,
        tags: List[Tag] = None,
    ):
        """
        Constructor for the Post class.

        Args:
            id (str): id of the post
            title (str): title of the post
            content (str): content of the post
            author (str): author of the post
            date (str, optional): date of the post. Defaults to None.
            comments (List[Comment], optional): comments on the post. Defaults to None.
            categories (List[Category], optional): categories of the post. Defaults to None.
            tags (List[Tag], optional): tags of the post. Defaults to None.
        """
        self.id = post_id
        self.title = title
        self.content = content
        self.author = author
        self.date = date if date else datetime.now(UTC).isoformat()
        self.comments = comments if comments is not None else []
        self.categories = categories if categories is not None else []
        self.tags = tags if tags is not None else []

    def to_dict(self) -> dict:
        """
        Convert the post to a dictionary.

        Returns:
            dict:  A dictionary representation of the post.
        """
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

    def add_comment(self, content: str) -> Comment:
        """
        Add a comment to the post.

        Args:
            content (str): The content of the comment.

        Returns:
            Comment: The comment object.
        """
        new_comment = Comment(uuid.uuid4().hex, self.id, content)
        self.comments.append(new_comment)
        return new_comment

    def add_category(self, name: str) -> Category:
        """
        Add a category to the post.

        Args:
            name (str): The name of the category.

        Returns:
            Category: The category object.
        """
        new_category = Category(uuid.uuid4().hex, name)
        self.categories.append(new_category)
        return new_category

    def add_tag(self, name: str) -> Tag:
        """
        Add a tag to the post.

        Args:
            name (str): The name of the tag.

        Returns:
            Tag: The tag object.
        """
        new_tag = Tag(uuid.uuid4().hex, name)
        self.tags.append(new_tag)
        return new_tag


class PostList:
    """A class to represent a list of blog posts."""

    def __init__(self, file_path: str = POSTS_FILE) -> None:
        """
        Constructor for the PostList class.

        Args:
            file_path (str, optional): The path to the file where the
            posts are stored. Defaults to POSTS_FILE.
        """
        self.file_path = file_path
        self.posts = self.load_posts()

    def load_posts(self) -> List[Post]:
        """
        Load the posts from the file.

        Returns:
            List[Post]: A list of post objects.
        """
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as file:
                    posts_data = json.load(file)
                    return [Post(**post_data) for post_data in posts_data]
            except (IOError, json.JSONDecodeError):
                return []
        return []

    def save_posts(self) -> None:
        """Save the posts to the file."""
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump([post.to_dict() for post in self.posts], file, indent=4)

    def get_all(self) -> List[dict]:
        """Get all the posts.

        Returns:
            List[dict]: A list of post dictionaries.
        """
        return [post.to_dict() for post in self.posts]

    # pylint: disable=too-many-arguments

    def add_post(
        self,
        title: str,
        content: str,
        author: str,
        categories: List[Category] = None,
        tags: List[Tag] = None,
    ) -> Post:
        """Add a new post.

        Args:
            title (str): title of the post
            content (str):  content of the post
            author (str):   author of the post
            categories (List[Category], optional): categories of the post. Defaults to None.
            tags (List[Tag], optional): tags of the post. Defaults to None.

        Returns:
            Post: The post object.
        """
        new_id = uuid.uuid4().hex
        new_post = Post(
            new_id, title, content, author, categories=categories, tags=tags
        )
        self.posts.append(new_post)
        self.save_posts()
        return new_post

    def find_post_by_id(self, post_id: str) -> Post:
        """Find a post by its id."""
        return next((post for post in self.posts if post.id == post_id), None)

    def delete_post(self, post_id: str) -> Post:
        """Delete a post by its id."""
        post = self.find_post_by_id(post_id)
        if post:
            self.posts = [post for post in self.posts if post.id != post_id]
            self.save_posts()
            return post
        raise PostNotFoundException(f"Post with ID {post_id} not found")

    def update_post(self, post_id: str, title: str, content: str, author: str) -> Post:
        """
        Update a post.

        Args:
            post_id (str): id of the post
            title (str): title of the post
            content (str): content of the post
            author (str): author of the post

        Raises:
            PostNotFoundException: Raised when a post is not found.

        Returns:
            Post: The updated post object.
        """
        post = self.find_post_by_id(post_id)
        if post:
            post.title = title
            post.content = content
            post.author = author
            post.date = datetime.utcnow().isoformat()  # Update the date when editing
            self.save_posts()
            return post
        raise PostNotFoundException(f"Post with ID {post_id} not found")

    def sort_posts(self, sort_by: str = None, direction: str = "asc") -> List[Post]:
        """
        Sort the posts.

        Args:
            sort_by (str, optional): The field to sort by. Defaults to None.
            direction (str, optional): The sort direction. Defaults to "asc".

        Raises:
            InvalidDataException: Raised when the data provided is invalid.

        Returns:
            List[Post]: A list of sorted post objects.
        """

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
    def validate_post_data(data: dict) -> None:
        """
        Validate the post data.

        Args:
            data (dict): The data to validate.

        Raises:
            InvalidDataException: Raised when the data provided is invalid.
        """
        required_fields = ["title", "content", "author"]

        # Check if the data is None or empty
        if not data:
            raise InvalidDataException("No data provided")

        # Check for missing fields or empty values
        for field in required_fields:
            if field not in data or not data[field]:
                raise InvalidDataException(f"Missing or empty field: {field}")
