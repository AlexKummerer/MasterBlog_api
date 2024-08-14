import uuid
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes


class Post:
    def __init__(self, id, title, content):
        self.id = id
        self.title = title
        self.content = content

    def to_dict(self):
        return {"id": self.id, "title": self.title, "content": self.content}


class PostList:
    def __init__(self):
        self.posts = [
            Post("1", "First post", "This is the first post."),
            Post("2", "Second post", "This is the second post."),
        ]

    def get_all(self):
        return [post.to_dict() for post in self.posts]

    def add_post(self, title, content):
        new_id = uuid.uuid4().hex
        new_post = Post(new_id, title, content)
        self.posts.append(new_post)
        return new_post

    def get_next_id(self):
        return str(int(max(post.id for post in self.posts)) + 1)


post_list = PostList()


@app.route("/api/posts", methods=["GET"])
def get_posts():
    return jsonify(post_list.get_all())


@app.route("/api/posts", methods=["POST"])
def create_post():
    try:
        data = request.get_json()
        if (
            not data
            or "title" not in data
            or "content" not in data
            or not data["title"]
            or not data["content"]
        ):
            return jsonify({"error": "Missing title or content"}), 400

        new_post = post_list.add_post(data["title"], data["content"])

        return jsonify(new_post.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/posts/<string:post_id>", methods=["DELETE"])
def delete_post(post_id):
    try:
        post = next((post for post in post_list.posts if post.id == post_id), None)
        if not post:
            return jsonify({"error": "Post not found"}), 404

        post_list.posts = [post for post in post_list.posts if post.id != post_id]

        return jsonify({"message": "Post deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/posts/<string:post_id>", methods=["PUT"])
def update_post(post_id):
    try:
        post = next((post for post in post_list.posts if post.id == post_id), None)
        if not post:
            return jsonify({"error": "Post not found"}), 404

        data = request.get_json()
        if (
            not data
            or "title" not in data
            or "content" not in data
            or not data["title"]
            or not data["content"]
        ):
            return jsonify({"error": "Missing title or content"}), 400

        post.title = data["title"]
        post.content = data["content"]

        return jsonify(post.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
