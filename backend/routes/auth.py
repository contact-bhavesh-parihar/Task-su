from flask import Blueprint, request, jsonify
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

from ..model import db, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['POST'])
def signup():

    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({
            "error": "All fields are required"
        }), 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({
            "error": "Email already exists"
        }), 400

    hashed_password = generate_password_hash(password)

    new_user = User(
        name=name,
        email=email,
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully"
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():

    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({
            "error": "Email and password required"
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "error": "Invalid credentials"
        }), 401

    if not check_password_hash(user.password, password):
        return jsonify({
            "error": "Invalid credentials"
        }), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful",
        "token": access_token,
        "user_id": user.id,
        "name": user.name
    }), 200
