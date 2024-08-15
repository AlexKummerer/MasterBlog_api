import uuid
import os
import json
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
)
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger, swag_from

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = str(os.urandom(24))
CORS(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)
swagger = Swagger(app)

users = {}

POSTS_FILE = "posts.json"  # File to store posts


# Models


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
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
        self, id, title, content, author, date=None, categories=None, tags=None
    ):
        self.id = id
        self.title = title
        self.content = content
        self.author = author
        self.date = date if date else datetime.utcnow().isoformat()
        self.comments = []
        self.categories = categories if categories else []
        self.tags = tags if tags else []

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


def paginate_results(results, page, per_page, base_url, query_params=None):
    start = (page - 1) * per_page
    end = start + per_page
    paginated_results = results[start:end]

    next_url = None
    if end < len(results):
        query_params = query_params or {}
        query_params.update({"page": page + 1, "per_page": per_page})
        query_string = "&".join(
            [f"{key}={value}" for key, value in query_params.items()]
        )
        next_url = f"{base_url}?{query_string}"

    return paginated_results, next_url


post_list = PostList()

# Routes


@app.route("/api/register", methods=["POST"])
@swag_from(
    {
        "summary": "Register a new user",
        "description": "Create a new user account by providing a username and password.",
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "example": "john_doe"},
                        "password": {"type": "string", "example": "password123"},
                    },
                    "required": ["username", "password"],
                },
            }
        ],
        "responses": {
            201: {"description": "User registered successfully"},
            400: {"description": "User already exists or missing username/password"},
            500: {"description": "Server error"},
        },
    }
)
def register():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400
        if username in users:
            return jsonify({"error": "User already exists"}), 400

        users[username] = User(username, password)
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/login", methods=["POST"])
@swag_from(
    {
        "summary": "Login a user and return a JWT token",
        "description": "This endpoint allows a user to log in by providing a valid username and password.",
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "example": "john_doe"},
                        "password": {"type": "string", "example": "password123"},
                    },
                    "required": ["username", "password"],
                },
            }
        ],
        "responses": {
            200: {
                "description": "User logged in successfully",
                "schema": {
                    "type": "object",
                    "properties": {"access_token": {"type": "string"}},
                },
            },
            400: {"description": "Missing username/password"},
            401: {"description": "Invalid credentials"},
            500: {"description": "Server error"},
        },
    }
)
def login():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400

        user = users.get(username)
        if user and user.check_password(password):
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token), 200

        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/posts", methods=["GET"])
@jwt_required()
@limiter.limit("5 per minute")
@swag_from(
    {
        "summary": "Get a list of posts",
        "description": "Retrieve a paginated list of posts. Requires JWT authentication.",
        "parameters": [
            {
                "name": "Authorization",
                "in": "header",
                "type": "string",
                "required": True,
                "description": "JWT token for authorization in the format Bearer <token>",
            },
            {
                "name": "page",
                "in": "query",
                "type": "integer",
                "required": False,
                "default": 1,
                "description": "Page number for pagination",
            },
            {
                "name": "per_page",
                "in": "query",
                "type": "integer",
                "required": False,
                "default": 10,
                "description": "Number of posts per page",
            },
        ],
        "responses": {
            200: {
                "description": "A list of paginated posts",
                "schema": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"type": "object"},
                        },
                        "next_url": {"type": "string"},
                    },
                },
            },
            400: {"description": "Invalid pagination parameters"},
            500: {"description": "Server error"},
        },
    }
)
def get_posts():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

        if page < 1 or per_page < 1:
            return (
                jsonify({"error": "Page and per_page must be positive integers"}),
                400,
            )

        results = post_list.get_all()
        paginated_posts, next_url = paginate_results(
            results, page, per_page, request.base_url
        )

        return jsonify({"results": paginated_posts, "next_url": next_url}), 200
    except ValueError:
        return jsonify({"error": "Page and per_page must be integers"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/posts", methods=["POST"])
@jwt_required()
@swag_from(
    {
        "summary": "Create a new post",
        "description": "Create a new post. Requires JWT authentication.",
        "parameters": [
            {
                "name": "Authorization",
                "in": "header",
                "type": "string",
                "required": True,
                "description": "JWT token for authorization in the format Bearer <token>",
            },
            {
                "name": "body",
                "in": "body",
                "schema": {
                    "properties": {
                        "title": {"type": "string", "required": True},
                        "content": {"type": "string", "required": True},
                        "author": {"type": "string", "required": True},
                    },
                },
            },
        ],
        "responses": {
            201: {
                "description": "Post created successfully",
                "schema": {"type": "object", "properties": {"id": {"type": "string"}}},
            },
            400: {"description": "Missing title, content, or author"},
            500: {"description": "Server error"},
        },
    }
)
def create_post():
    try:
        data = request.get_json()
        post_list.validate_post_data(data)
        new_post = post_list.add_post(data["title"], data["content"], data["author"])
        return jsonify(new_post.to_dict()), 201
    except InvalidDataException as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/posts/<string:post_id>", methods=["DELETE"])
@jwt_required()
@swag_from(
    {
        "summary": "Delete a post",
        "description": "Delete a post by ID. Requires JWT authentication.",
        "parameters": [
            {
                "name": "Authorization",
                "in": "header",
                "type": "string",
                "required": True,
                "description": "JWT token for authorization in the format Bearer <token>",
            },
            {"name": "post_id", "in": "path", "type": "string", "required": True},
        ],
        "responses": {
            200: {"description": "Post deleted successfully"},
            404: {"description": "Post not found"},
            500: {"description": "Server error"},
        },
    }
)
def delete_post(post_id):
    try:
        post_list.delete_post(post_id)
        return jsonify({"message": "Post deleted"}), 200
    except PostNotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/posts/<string:post_id>", methods=["PUT"])
@jwt_required()
@swag_from(
    {
        "summary": "Update a post",
        "description": "Update a post by ID. Requires JWT authentication.",
        "parameters": [
            {
                "name": "Authorization",
                "in": "header",
                "type": "string",
                "required": True,
                "description": "JWT token for authorization in the format Bearer <token>",
            },
            {"name": "post_id", "in": "path", "type": "string", "required": True},
            {
                "name": "body",
                "in": "body",
                "schema": {
                    "properties": {
                        "title": {"type": "string", "required": True},
                        "content": {"type": "string", "required": True},
                        "author": {"type": "string", "required": True},
                    },
                    "required": ["title", "content", "author"],
                },
            },
        ],
        "responses": {
            200: {"description": "Post updated successfully"},
            404: {"description": "Post not found"},
            400: {"description": "Invalid data provided"},
            500: {"description": "Server error"},
        },
    }
)
def update_post(post_id):
    try:
        data = request.get_json()
        post_list.validate_post_data(data)
        updated_post = post_list.update_post(
            post_id, data["title"], data["content"], data["author"]
        )
        return jsonify(updated_post.to_dict()), 200
    except PostNotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except InvalidDataException as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/posts/search", methods=["GET"])
@jwt_required()
@swag_from(
    {
        "summary": "Search for posts",
        "description": "Search posts by query string. Requires JWT authentication.",
        "parameters": [
            {
                "name": "Authorization",
                "in": "header",
                "type": "string",
                "required": True,
                "description": "JWT token for authorization in the format Bearer <token>",
            },
            {"name": "query", "in": "query", "type": "string", "required": True},
            {
                "name": "page",
                "in": "query",
                "type": "integer",
                "required": False,
                "default": 1,
                "description": "Page number for pagination",
            },
            {
                "name": "per_page",
                "in": "query",
                "type": "integer",
                "required": False,
                "default": 10,
                "description": "Number of posts per page",
            },
        ],
        "responses": {
            200: {
                "description": "A list of paginated search results",
                "schema": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"type": "object"},
                        },
                        "next_url": {"type": "string"},
                    },
                },
            },
            400: {"description": "Invalid pagination parameters"},
            500: {"description": "Server error"},
        },
    }
)
def search_posts():
    try:
        query = request.args.get("query")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

        if not query:
            return jsonify({"error": "Missing query parameter"}), 400

        results = [
            post.to_dict()
            for post in post_list.posts
            if query.lower() in post.title.lower()
            or query.lower() in post.content.lower()
            or query.lower() in post.author.lower()
        ]

        paginated_results, next_url = paginate_results(
            results, page, per_page, request.base_url, query_params={"query": query}
        )

        return jsonify({"results": paginated_results, "next_url": next_url}), 200
    except ValueError:
        return jsonify({"error": "Page and per_page must be integers"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/posts/sort", methods=["GET"])
@jwt_required()
@swag_from(
    {
        "summary": "Sort posts",
        "description": "Sort posts by a specified field (title, content, author, or date) and order. Requires JWT authentication.",
        "parameters": [
            {
                "name": "Authorization",
                "in": "header",
                "type": "string",
                "required": True,
                "description": "JWT token for authorization in the format Bearer <token>",
            },
            {
                "name": "sort_by",
                "in": "query",
                "type": "string",
                "required": False,
                "enum": ["title", "content", "author", "date"],
                "description": "Field to sort by (title, content, author, or date)",
            },
            {
                "name": "direction",
                "in": "query",
                "type": "string",
                "required": False,
                "enum": ["asc", "desc"],
                "default": "asc",
                "description": "Sort direction (ascending or descending)",
            },
            {
                "name": "page",
                "in": "query",
                "type": "integer",
                "required": False,
                "default": 1,
                "description": "Page number for pagination",
            },
            {
                "name": "per_page",
                "in": "query",
                "type": "integer",
                "required": False,
                "default": 10,
                "description": "Number of posts per page",
            },
        ],
        "responses": {
            200: {
                "description": "A list of sorted and paginated posts",
                "schema": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"type": "object"},
                        },
                        "next_url": {"type": "string"},
                    },
                },
            },
            400: {"description": "Invalid parameters provided"},
            500: {"description": "Server error"},
        },
    }
)
def sort_posts():
    try:
        sort_by = request.args.get("sort_by")
        direction = request.args.get("direction", "asc")
        sorted_posts = post_list.sort_posts(sort_by, direction)
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

        paginated_results, next_url = paginate_results(
            sorted_posts,
            page,
            per_page,
            request.base_url,
            query_params={"sort_by": sort_by, "direction": direction},
        )

        return jsonify({"results": paginated_results, "next_url": next_url}), 200
    except InvalidDataException as e:
        return jsonify({"error": f"Invalid parameters: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
