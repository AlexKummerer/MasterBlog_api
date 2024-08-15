# app.py
import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger
from routes.auth import auth_bp
from routes.posts import posts_bp

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = str(os.urandom(24))
CORS(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)
swagger = Swagger(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(posts_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
