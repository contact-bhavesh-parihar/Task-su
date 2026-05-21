from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from model import db, Task, ProjectMember

tasks_bp = Blueprint('tasks', __name__)


# CREATE TASK
@tasks_bp.route('/create', methods=['POST'])
@jwt_required()
def create_task():

    data = request.get_json()

    title = data.get('title')
    description = data.get('description')
    project_id = data.get('project_id')
    assigned_to = data.get('assigned_to')

    current_user_id = int(get_jwt_identity())

    if not title or not project_id:
        return jsonify({
            "error": "Title and project_id required"
        }), 400

    # check membership
    membership = ProjectMember.query.filter_by(
        project_id=project_id,
        user_id=current_user_id
    ).first()

    if not membership:
        return jsonify({
            "error": "You are not part of this project"
        }), 403

    new_task = Task(
        title=title,
        description=description,
        project_id=project_id,
        assigned_to=assigned_to,
        created_by=current_user_id
    )

    db.session.add(new_task)
    db.session.commit()

    return jsonify({
        "message": "Task created successfully"
    }), 201


# GET TASKS OF PROJECT
@tasks_bp.route('/project/<int:project_id>', methods=['GET'])
@jwt_required()
def get_tasks(project_id):

    current_user_id = int(get_jwt_identity())

    membership = ProjectMember.query.filter_by(
        project_id=project_id,
        user_id=current_user_id
    ).first()

    if not membership:
        return jsonify({
            "error": "Access denied"
        }), 403

    tasks = Task.query.filter_by(project_id=project_id).all()

    tasks_data = []

    for task in tasks:

        tasks_data.append({
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "assigned_to": task.assigned_to
        })

    return jsonify(tasks_data), 200


# UPDATE TASK STATUS
@tasks_bp.route('/update-status/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task_status(task_id):

    data = request.get_json()

    new_status = data.get('status')

    current_user_id = int(get_jwt_identity())

    task = Task.query.get(task_id)

    if not task:
        return jsonify({
            "error": "Task not found"
        }), 404

    # only assigned user can update
    if task.assigned_to != current_user_id:
        return jsonify({
            "error": "You can update only your tasks"
        }), 403

    task.status = new_status

    db.session.commit()

    return jsonify({
        "message": "Task status updated"
    }), 200


# DELETE TASK
@tasks_bp.route('/delete/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):

    current_user_id = int(get_jwt_identity())

    task = Task.query.get(task_id)

    if not task:
        return jsonify({
            "error": "Task not found"
        }), 404

    # only creator can delete
    if task.created_by != current_user_id:
        return jsonify({
            "error": "Only creator can delete task"
        }), 403

    db.session.delete(task)
    db.session.commit()

    return jsonify({
        "message": "Task deleted successfully"
    }), 200
