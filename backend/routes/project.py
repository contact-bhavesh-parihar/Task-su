from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..model import db, Project, ProjectMember, User

projects_bp = Blueprint('projects', __name__)


# CREATE PROJECT
@projects_bp.route('/create', methods=['POST'])
@jwt_required()
def create_project():

    data = request.get_json()

    project_name = data.get('name')

    if not project_name:
        return jsonify({
            "error": "Project name is required"
        }), 400

    current_user_id = int(get_jwt_identity())

    new_project = Project(
        name=project_name,
        created_by=current_user_id
    )

    db.session.add(new_project)
    db.session.commit()

    # creator automatically becomes admin
    project_member = ProjectMember(
        project_id=new_project.id,
        user_id=current_user_id,
        role='admin'
    )

    db.session.add(project_member)
    db.session.commit()

    return jsonify({
        "message": "Project created successfully"
    }), 201


# GET ALL PROJECTS OF USER
@projects_bp.route('/', methods=['GET'])
@jwt_required()
def get_projects():

    current_user_id = int(get_jwt_identity())

    memberships = ProjectMember.query.filter_by(
        user_id=current_user_id
    ).all()

    projects_data = []

    for membership in memberships:

        project = Project.query.get(membership.project_id)

        projects_data.append({
            "project_id": project.id,
            "project_name": project.name,
            "role": membership.role
        })

    return jsonify(projects_data), 200


# ADD MEMBER TO PROJECT
@projects_bp.route('/add-member', methods=['POST'])
@jwt_required()
def add_member():

    data = request.get_json()

    project_id = data.get('project_id')
    user_email = data.get('email')
    role = data.get('role', 'member')

    current_user_id = int(get_jwt_identity())

    # check if current user is admin
    admin_check = ProjectMember.query.filter_by(
        project_id=project_id,
        user_id=current_user_id,
        role='admin'
    ).first()

    if not admin_check:
        return jsonify({
            "error": "Only admins can add members"
        }), 403

    user = User.query.filter_by(email=user_email).first()

    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    existing_member = ProjectMember.query.filter_by(
        project_id=project_id,
        user_id=user.id
    ).first()

    if existing_member:
        return jsonify({
            "error": "User already added"
        }), 400

    new_member = ProjectMember(
        project_id=project_id,
        user_id=user.id,
        role=role
    )

    db.session.add(new_member)
    db.session.commit()

    return jsonify({
        "message": "Member added successfully"
    }), 201
