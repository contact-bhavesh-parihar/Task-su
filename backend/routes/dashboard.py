from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..model import ProjectMember, Task

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def dashboard_stats():

    current_user_id = int(get_jwt_identity())

    # user's projects
    memberships = ProjectMember.query.filter_by(
        user_id=current_user_id
    ).all()

    project_ids = [m.project_id for m in memberships]

    total_projects = len(project_ids)

    total_tasks = Task.query.filter(
        Task.project_id.in_(project_ids)
    ).count()

    completed_tasks = Task.query.filter(
        Task.project_id.in_(project_ids),
        Task.status == 'Completed'
    ).count()

    pending_tasks = Task.query.filter(
        Task.project_id.in_(project_ids),
        Task.status != 'Completed'
    ).count()

    return jsonify({
        "total_projects": total_projects,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks
    }), 200
