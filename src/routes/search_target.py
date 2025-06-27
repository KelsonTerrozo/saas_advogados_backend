from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.search_target import SearchTarget
from src.models.user import User

search_target_bp = Blueprint("search_target_bp", __name__)

@search_target_bp.route("/search-targets", methods=["POST"])
def create_search_target():
    data = request.get_json()
    user_id = data.get("user_id")
    oab_number = data.get("oab_number")
    oab_uf = data.get("oab_uf")

    if not user_id or not oab_number or not oab_uf:
        return jsonify({"message": "User ID, OAB number, and OAB UF are required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    new_search_target = SearchTarget(user_id=user_id, oab_number=oab_number, oab_uf=oab_uf)
    db.session.add(new_search_target)
    db.session.commit()

    return jsonify({"message": "Search target created successfully", "id": new_search_target.id}), 201

@search_target_bp.route("/search-targets", methods=["GET"])
def get_search_targets():
    search_targets = SearchTarget.query.all()
    result = []
    for target in search_targets:
        result.append({
            "id": target.id,
            "user_id": target.user_id,
            "username": target.user.username,
            "oab_number": target.oab_number,
            "oab_uf": target.oab_uf,
            "is_active": target.is_active
        })
    return jsonify(result), 200

@search_target_bp.route("/search-targets/<int:target_id>", methods=["GET"])
def get_search_target(target_id):
    search_target = SearchTarget.query.get(target_id)
    if not search_target:
        return jsonify({"message": "Search target not found"}), 404
    return jsonify({
        "id": search_target.id,
        "user_id": search_target.user_id,
        "username": search_target.user.username,
        "oab_number": search_target.oab_number,
        "oab_uf": search_target.oab_uf,
        "is_active": search_target.is_active
    }), 200

@search_target_bp.route("/search-targets/<int:target_id>", methods=["PUT"])
def update_search_target(target_id):
    search_target = SearchTarget.query.get(target_id)
    if not search_target:
        return jsonify({"message": "Search target not found"}), 404

    data = request.get_json()
    search_target.oab_number = data.get("oab_number", search_target.oab_number)
    search_target.oab_uf = data.get("oab_uf", search_target.oab_uf)
    search_target.is_active = data.get("is_active", search_target.is_active)
    db.session.commit()

    return jsonify({"message": "Search target updated successfully"}), 200

@search_target_bp.route("/search-targets/<int:target_id>", methods=["DELETE"])
def delete_search_target(target_id):
    search_target = SearchTarget.query.get(target_id)
    if not search_target:
        return jsonify({"message": "Search target not found"}), 404
    db.session.delete(search_target)
    db.session.commit()
    return jsonify({"message": "Search target deleted successfully"}), 204

