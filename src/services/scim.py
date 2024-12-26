from flask import Blueprint
from flask import jsonify, make_response, request, session
from functools import wraps
from services.database import db
from models.models import User
import re
from sqlalchemy import func
from app_config import SCIM_SECRET

scim_router = Blueprint('scim', __name__, template_folder='templates')

def auth_required(func):
    """Flask decorator to require the presence of a valid Authorization header."""
    @wraps(func)
    def check_auth(*args, **kwargs):
        try:
            if request.headers["Authorization"].split("Bearer ")[1] != SCIM_SECRET:
                return make_response(jsonify({
                    "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                    "status": "403",
                    "detail": "Unauthorized"
                }), 403, {"Content-Type": "application/scim+json"})
        except KeyError:
            return make_response(jsonify({
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                "status": "403",
                "detail": "Unauthorized"
            }), 403, {"Content-Type": "application/scim+json"})
        return func(*args, **kwargs)
    return check_auth

@scim_router.before_request
def before_request():
    """Ensure requests have the correct Content-Type."""
    if request.method in ['POST', 'PUT', 'PATCH']:
        if 'application/scim+json' not in request.headers.get('Content-Type', ''):
            return make_response(jsonify({
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                "detail": "Content-Type must be application/scim+json"
            }), 415, {"Content-Type": "application/scim+json"})

@scim_router.after_request
def after_request(response):
    """Add the appropriate SCIM headers to all responses."""
    response.headers['Content-Type'] = 'application/scim+json'
    return response

@scim_router.route("/scim/v2/Schemas")
def get_schemas():
    """Get SCIM Schemas"""
    schemas = [
        {
            "id": "urn:ietf:params:scim:schemas:core:2.0:User",
            "name": "User",
            "description": "Core User schema",
            "attributes": [
                {"name": "id", "type": "string", "multiValued": False, "required": True, "mutability": "readOnly"},
                {"name": "userName", "type": "string", "multiValued": False, "required": True, "mutability": "readWrite"},
                {"name": "name", "type": "complex", "multiValued": False, "required": False, "mutability": "readWrite", "subAttributes": [
                    {"name": "givenName", "type": "string", "multiValued": False, "mutability": "readWrite"},
                    {"name": "middleName", "type": "string", "multiValued": False, "mutability": "readWrite"},
                    {"name": "familyName", "type": "string", "multiValued": False, "mutability": "readWrite"}
                ]},
                {"name": "displayName", "type": "string", "multiValued": False, "mutability": "readWrite"},
                {"name": "locale", "type": "string", "multiValued": False, "mutability": "readWrite"},
                {"name": "externalId", "type": "string", "multiValued": False, "mutability": "readWrite"},
                {"name": "active", "type": "boolean", "multiValued": False, "mutability": "readWrite"},
                {"name": "groups", "type": "complex", "multiValued": True, "mutability": "readOnly", "subAttributes": [
                    {"name": "display", "type": "string", "multiValued": False, "mutability": "readOnly"},
                    {"name": "value", "type": "string", "multiValued": False, "mutability": "readOnly"}
                ]},
                {"name": "meta", "type": "complex", "multiValued": False, "mutability": "readOnly", "subAttributes": [
                    {"name": "resourceType", "type": "string", "multiValued": False, "mutability": "readOnly"},
                    {"name": "created", "type": "string", "multiValued": False, "mutability": "readOnly"},
                    {"name": "lastModified", "type": "string", "multiValued": False, "mutability": "readOnly"}
                ]}
            ]
        },
        {
            "id": "urn:ietf:params:scim:schemas:core:2.0:Group",
            "name": "Group",
            "description": "Core Group schema",
            "attributes": [
                {"name": "id", "type": "string", "multiValued": False, "required": True, "mutability": "readOnly"},
                {"name": "displayName", "type": "string", "multiValued": False, "required": True, "mutability": "readWrite"},
                {"name": "members", "type": "complex", "multiValued": True, "mutability": "readWrite", "subAttributes": [
                    {"name": "value", "type": "string", "multiValued": False, "mutability": "readWrite"},
                    {"name": "display", "type": "string", "multiValued": False, "mutability": "readWrite"}
                ]},
                {"name": "meta", "type": "complex", "multiValued": False, "mutability": "readOnly", "subAttributes": [
                    {"name": "resourceType", "type": "string", "multiValued": False, "mutability": "readOnly"},
                    {"name": "created", "type": "string", "multiValued": False, "mutability": "readOnly"},
                    {"name": "lastModified", "type": "string", "multiValued": False, "mutability": "readOnly"}
                ]}
            ]
        }
    ]

    return make_response(
        jsonify({
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "totalResults": len(schemas),
            "Resources": schemas
        }),
        200
    )

@scim_router.route("/scim/v2/Users", methods=["GET"])
@auth_required
def get_users():
    """Get SCIM Users"""
    start_index = int(request.args.get('startIndex', 1))
    count = int(request.args.get('count', 10))

    if "filter" in request.args:
        filter_parts = request.args["filter"].split(" ")
        if len(filter_parts) == 3 and filter_parts[0] == "userName" and filter_parts[1] == "eq":
            filter_value = filter_parts[2].strip('"').lower()
            users = User.query.filter(func.lower(User.userName) == filter_value).all()
            total_results = len(users)
        else:
            users = []
            total_results = 0
    else:
        pagination = User.query.paginate(start_index, count, False)
        users = pagination.items
        total_results = pagination.total

    serialized_users = [u.serialize() for u in users]

    return make_response(
        jsonify({
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "totalResults": total_results,
            "startIndex": start_index,
            "itemsPerPage": count,
            "Resources": serialized_users
        }),
        200
    )

@scim_router.route("/scim/v2/Users/<string:user_id>", methods=["GET"])
@auth_required
def get_user(user_id):
    """Get SCIM User"""
    user = User.query.get(user_id)
    if not user:
        return make_response(
            jsonify({
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                "detail": "User not found",
                "status": 404
            }),
            404
        )
    
    return jsonify(user.serialize())

def format_attr(input_str):
    input_str = input_str.replace('.', '_')
    return re.sub(r'\[.*?\]', '', input_str)

@scim_router.route("/scim/v2/Users/<string:user_id>", methods=["PATCH"])
@auth_required
def update_user(user_id):
    """Update SCIM User"""
    user = User.query.get(user_id)

    if not user:
        return make_response(
            jsonify(
                {
                    "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                    "detail": "User not found",
                    "status": 404,
                }
            ),
            404,
        )
    else:
        print(request.json)
        for operation in request.json["Operations"]:
            # make the operation
            op = operation.get("op").lower()
            path = operation.get("path")
            value = operation.get("value")

            if not op:
                return make_response(
                    jsonify(
                        {
                            "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                            "detail": "Operation must include 'op' and 'path'.",
                            "status": 400,
                        }
                    ),
                    400,
                )

            try:
                if not path:
                    # Replace the entire user object
                    if not isinstance(value, dict):
                        raise AttributeError
                    if op == "replace" or op == "add":
                        # Update each attribute in the user object
                        for attr, attr_value in value.items():
                            attr = format_attr(attr)
                            # remove point in attribute name and add a maj to next letter
                            if hasattr(user, attr):
                                if isinstance(getattr(user, attr), bool):
                                    attr_value = attr_value.lower() == "true" if isinstance(attr_value, str) else bool(attr_value)
                                setattr(user, attr, attr_value)
                            else:
                                raise AttributeError
                elif path:
                    # Normalize path for attribute matching
                    attribute = path.split(":")[-1]  # Get the attribute name after any namespace prefixes
                    attribute = format_attr(attribute)

                    if op == "replace" or op == "add":
                        if hasattr(user, attribute):
                            if isinstance(getattr(user, attribute), bool):
                                value = value.lower() == "true" if isinstance(value, str) else bool(value)
                            setattr(user, attribute, value)
                        else:
                            raise AttributeError
                    elif op == "remove":
                        if hasattr(user, attribute):
                            setattr(user, attribute, None)
                        else:
                            raise AttributeError
                    else:
                        raise NotImplementedError
            except AttributeError:
                return make_response(
                    jsonify(
                        {
                            "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                            "detail": f"Attribute '{attr}' not found on user.",
                            "status": 400,
                        }
                    ),
                    400,
                )
            except NotImplementedError:
                return make_response(
                    jsonify(
                        {
                            "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                            "detail": f"Unsupported operation: {op}",
                            "status": 400,
                        }
                    ),
                    400,
                )
        db.session.commit()
        return make_response(jsonify(user.serialize()), 200)

@scim_router.route("/scim/v2/Users/<string:user_id>", methods=["DELETE"])
@auth_required
def delete_user(user_id):
    """Delete SCIM User"""
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return make_response("", 204)
