"""
    module for posts CRUD operations

    This module contains routes for creating, reading, updating, and deleting posts.
    It also contains routes for searching and sorting posts.
    
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from flasgger import swag_from
from models import PostList, InvalidDataException, PostNotFoundException
from routes.utils import paginate_results

posts_bp = Blueprint("posts", __name__)

post_list = PostList()


@posts_bp.route("/api/v1/posts", methods=["GET"])
@jwt_required()
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
def get_posts() -> str:
    """
    Get a list of posts

    Returns:
        str: A JSON response containing a list of paginated posts
    """
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
    # pylint: disable=broad-exception-caught
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@posts_bp.route("/api/v1/posts", methods=["POST"])
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
def create_post() -> str:
    """
    Create a new post

    Returns:
        str: A JSON response containing the newly created post
    """
    try:
        data = request.get_json()
        post_list.validate_post_data(data)
        new_post = post_list.add_post(data["title"], data["content"], data["author"])
        return jsonify(new_post.to_dict()), 201
    except InvalidDataException as e:
        return jsonify({"error": str(e)}), 400
        # pylint: disable=broad-exception-caught
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@posts_bp.route("/api/v1/posts/<string:post_id>", methods=["DELETE"])
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
def delete_post(post_id: str) -> str:
    """
    Delete a post

    Args:
        post_id (str):  post id

    Returns:
        str: A JSON response indicating the success or failure of the deletion
    """
    try:
        post_list.delete_post(post_id)
        return jsonify({"message": "Post deleted"}), 200
    except PostNotFoundException as e:
        return jsonify({"error": str(e)}), 404
    # pylint: disable=broad-exception-caught
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@posts_bp.route("/api/v1/posts/<string:post_id>", methods=["PUT"])
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
def update_post(post_id: str) -> str:
    """
    Update a post

    Args:
        post_id (str):  post id

    Returns:
        str: A JSON response containing the updated post
    """
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
    # pylint: disable=broad-exception-caught
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@posts_bp.route("/api/v1/posts/search", methods=["GET"])
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
def search_posts() -> str:
    """
    Search for posts

    Returns:
        str: A JSON response containing a list of paginated search results
    """
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
    # pylint: disable=broad-exception-caught
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@posts_bp.route("/api/v1/posts/sort", methods=["GET"])
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
def sort_posts() -> str:
    """
    Sort posts

    Returns:
        str: A JSON response containing a list of sorted and paginated posts

    """
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
    # pylint: disable=broad-exception-caught
    except Exception as e:
        return jsonify({"error": str(e)}), 500
