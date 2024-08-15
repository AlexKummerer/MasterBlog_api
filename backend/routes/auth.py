# routes/auth.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from flasgger import swag_from
from models import User


auth_bp = Blueprint('auth', __name__)

users = {}

@auth_bp.route("/api/register", methods=["POST"])
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


@auth_bp.route("/api/login", methods=["POST"])
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
