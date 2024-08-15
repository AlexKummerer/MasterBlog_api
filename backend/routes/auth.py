""" module for user authentication """

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from flasgger import swag_from
from flask_bcrypt import Bcrypt
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import User


auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()
users = {}


@auth_bp.route("/api/user", methods=["GET"])
@jwt_required()
@swag_from(
    {
        "summary": "Get the current logged-in user's information",
        "description": "Get the information of the current logged-in user.",
        "responses": {
            200: {
                "description": "User information retrieved successfully",
                "schema": {
                    "type": "object",
                    "properties": {"username": {"type": "string"}},
                },
            },
            401: {"description": "Unauthorized"},
        },
    }
)
def get_current_user():
    """
    Returns the current logged-in user's information.
    """
    current_user = (
        get_jwt_identity()
    )  # This will return the username stored in the JWT token
    return jsonify({"username": current_user}), 200


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
def register() -> str:
    """
    Register a new user

    Returns:
        str: A message indicating the success or failure of the registration
    """
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400
        if username in users:
            return jsonify({"error": "User already exists"}), 400

        users[username] = User(username, password, bcrypt=bcrypt)
        return jsonify({"message": "User registered successfully"}), 201
    except KeyError as ke:
        return jsonify({"error": f"Missing key: {str(ke)}"}), 400
    except TypeError as te:
        return jsonify({"error": f"Invalid input format: {str(te)}"}), 400
    # pylint: disable=broad-exception-caught
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/api/login", methods=["POST"])
@swag_from(
    {
        "summary": "Login a user and return a JWT token",
        "description": "This endpoint allows a user to log in by"
        + "providing a valid username and password.",
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
def login() -> str:
    """
    Login a user and return a JWT token

    Returns:
        str: A message indicating the success or failure of the login
    """
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400

        user = users.get(username)
        if user and user.check_password(password, bcrypt=bcrypt):
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token), 200

        return jsonify({"error": "Invalid credentials"}), 401
    except KeyError as ke:
        return jsonify({"error": f"Missing key: {str(ke)}"}), 400
    except TypeError as te:
        return jsonify({"error": f"Invalid input format: {str(te)} "}), 400
    # pylint: disable=broad-exception-caught
    except Exception as e:
        return jsonify({"error": str(e)}), 500
