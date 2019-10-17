import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
from .auth.auth import requires_auth, AuthError

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()


@app.route('/drinks')
def get_drinks():
    # GET drinks
    drinks = Drink.query.all()
    return jsonify({
        "success": True,
        "drinks": [d.short() for d in drinks]
    }), 200


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    # GET drinks detail
    drinks = Drink.query.all()
    return jsonify({
        "success": True,
        "drinks": [d.long() for d in drinks]
    }), 200


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(payload):
    # Post drinks
    body = request.get_json()
    drink = Drink()
    drink.recipe = json.dumps(body.get("recipe"))
    drink.title = body.get("title")
    drink.insert()
    return jsonify({
        "success": True,
        "drinks": drink.long()
    }), 200


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(*args, **kwargs):
    body = request.get_json()
    drink = Drink.query.filter_by(id=kwargs.get("id")).one_or_none()

    if not drink:
        abort(404, "Drink not found.")

    drink.recipe = body.get("recipe", drink.recipe)
    drink.title = body.get("title", drink.title)

    if isinstance(drink.recipe, list):
        drink.recipe = json.dumps(drink.recipe)

    drink.update()
    return jsonify({
        "success": True,
        "drinks": drink.long()
    }), 200


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(*args, **kwargs):
    # Delete drinks
    drink = Drink.query.filter_by(id=kwargs.get("id")).one_or_none()

    if not drink:
        abort(404, "Drink not found.")

    drink.delete()
    return jsonify({
        "success": True,
        "delete": kwargs.get("id")
    }), 200


# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(401)
def permission_error(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Authentication error"
    }), 401


@app.errorhandler(400)
def user_error(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": error.description
    }), 400


@app.errorhandler(AuthError)
def invalid_claims(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": error.__dict__
    }), 401
