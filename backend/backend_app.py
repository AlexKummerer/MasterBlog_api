import uuid
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "your_jwt_secret_key"
CORS(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
limiter = Limiter(app, key_func=lambda: get_jwt_identity())

users = {}


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
    def __init__(self, id, title, content, categories=None, tags=None):
        self.id = id
        self.title = title
        self.content = content
        self.comments = []
        self.categories = categories if categories else []
        self.tags = tags if tags else []

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
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


def paginate_results(results, page, per_page, base_url, query_params=None):
    start = (page - 1) * per_page
    end = start + per_page
    paginated_results = results[start:end]

    next_url = None
    if end < len(results):
        # Construct the next_url with all query parameters
        query_params = query_params or {}
        query_params.update({"page": page + 1, "per_page": per_page})
        query_string = "&".join(
            [f"{key}={value}" for key, value in query_params.items()]
        )
        next_url = f"{base_url}?{query_string}"

    return paginated_results, next_url


class PostList:
    def __init__(self):
        self.posts = [
            Post("1", "First post", "This is the first post."),
            Post("2", "Second post", "This is the second post."),
        ]

    def get_all(self):
        return [post.to_dict() for post in self.posts]

    def add_post(self, title, content, categories=None, tags=None):
        new_id = uuid.uuid4().hex
        new_post = Post(new_id, title, content, categories, tags)
        self.posts.append(new_post)
        return new_post

    def sort_posts(self, sort_by=None, direction="asc"):
        if sort_by:
            if sort_by not in ["title", "content"]:
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
            or not data["title"]
            or not data["content"]
        ):
            raise InvalidDataException("Missing title or content")


post_list = PostList()


@app.route("/api/register", methods=["POST"])
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
def create_post():
    try:
        data = request.get_json()
        post_list.validate_post_data(data)
        new_post = post_list.add_post(data["title"], data["content"])
        return jsonify(new_post.to_dict()), 201
    except InvalidDataException as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/posts/<string:post_id>", methods=["DELETE"])
@jwt_required()
def delete_post(post_id):
    try:
        post = next((post for post in post_list.posts if post.id == post_id), None)
        if not post:
            raise PostNotFoundException("Post not found")
        post_list.posts = [post for post in post_list.posts if post.id != post_id]
        return jsonify({"message": "Post deleted"}), 200
    except PostNotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/posts/<string:post_id>", methods=["PUT"])
@jwt_required()
def update_post(post_id):
    try:
        post = next((post for post in post_list.posts if post.id == post_id), None)
        if not post:
            raise PostNotFoundException("Post not found")
        data = request.get_json()
        post_list.validate_post_data(data)
        post.title = data["title"]
        post.content = data["content"]
        return jsonify(post.to_dict()), 200
    except PostNotFoundException as e:
        return jsonify({"error": str(e)}), 404
    except InvalidDataException as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/posts/search", methods=["GET"])
@jwt_required()
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
