from flask import Blueprint, request, jsonify
from models.project import Project
from database import db
from datetime import datetime
from sqlalchemy import cast, Date

project_bp = Blueprint('project', __name__)


# ✅ Create a new project
@project_bp.route("/create", methods=["POST"])
def create_project():
    data = request.get_json() or {}
    # require at least these:
    if not data.get("project_name") or not data.get("created_by"):
        return jsonify({"error": "Missing project_name or created_by"}), 400

    # validate your arrays
    subparts = data.get("project_subparts", [])
    assigned = data.get("assigned_ids", [])
    if not isinstance(subparts, list) or not isinstance(assigned, list):
        return jsonify({"error": "project_subparts and assigned_ids must be arrays"}), 400

    # build the model
    new_project = Project(
        project_name=data["project_name"].strip(),
        project_subparts=subparts,
        total_estimate_hrs=data.get("total_estimate_hrs", 0),
        total_elapsed_hrs=data.get("total_elapsed_hrs", 0),
        assigned_ids=assigned,
        created_by=data["created_by"],
        is_completed=data.get("is_completed", False),
        client_id=data.get("client_id", 1),
        # created_at is auto‐defaulted
    )

    db.session.add(new_project)
    db.session.flush()  # ← push INSERT & populate new_project.id
    project_id = new_project.id  # ← now safe to read
    db.session.commit()  # ← persist transaction

    return jsonify({
        "message": "Project created successfully",
        "project_id": project_id
    }), 201


# ✅ Get all projects
@project_bp.route('/all', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    project_list = [{
        'id': p.id,
        'project_name': p.project_name,
        'project_subparts': p.project_subparts,
        'total_estimate_hrs': p.total_estimate_hrs,
        'total_elapsed_hrs': p.total_elapsed_hrs,
        'assigned_ids': p.assigned_ids,
        'is_completed': p.is_completed,
        'created_by': p.created_by,
        'client_id': p.client_id,
        'created_at': p.created_at,
        'updated_at': p.updated_at
    } for p in projects]

    return jsonify({'projects': project_list, 'total_projects': len(project_list)}), 200


# ✅ Get single project by ID
@project_bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    return jsonify({
        'id': project.id,
        'project_name': project.project_name,
        'project_subparts': project.project_subparts,
        'total_estimate_hrs': project.total_estimate_hrs,
        'total_elapsed_hrs': project.total_elapsed_hrs,
        'assigned_ids': project.assigned_ids,
        'is_completed': project.is_completed,
        'created_by': project.created_by,
        'client_id': project.client_id,
        'created_at': project.created_at,
        'updated_at': project.updated_at
    }), 200


# ✅ Update a project
@project_bp.route('/update/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    data = request.get_json()

    if 'project_name' in data:
        project.project_name = data['project_name'].strip()

    if 'project_subparts' in data:
        if not isinstance(data['project_subparts'], list):
            return jsonify({'error': 'project_subparts must be an array'}), 400
        project.project_subparts = data['project_subparts']

    if 'total_estimate_hrs' in data:
        project.total_estimate_hrs = data['total_estimate_hrs']

    if 'total_elapsed_hrs' in data:
        project.total_elapsed_hrs = data['total_elapsed_hrs']

    if 'assigned_ids' in data:
        if not isinstance(data['assigned_ids'], list):
            return jsonify({'error': 'assigned_ids must be an array'}), 400
        project.assigned_ids = data['assigned_ids']

    if 'is_completed' in data:
        project.is_completed = data['is_completed']

    db.session.commit()

    return jsonify({'message': 'Project updated successfully'}), 200


# ✅ Delete a project
@project_bp.route('/delete/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    db.session.delete(project)
    db.session.commit()

    return jsonify({'message': 'Project deleted successfully'}), 200


# ✅ Filter projects (example)
@project_bp.route('/filter', methods=['GET'])
def filter_projects():
    created_by = request.args.get('created_by', type=int)
    assigned_id = request.args.get('assigned_id', type=int)
    project_name = request.args.get('project_name', type=str)
    start_date = request.args.get('start_date', type=str)
    end_date = request.args.get('end_date', type=str)
    offset = request.args.get('offset', type=int, default=0)

    query = Project.query

    if created_by:
        query = query.filter(Project.created_by == created_by)

    if assigned_id:
        query = query.filter(cast(Project.assigned_ids, str).like(f'%{assigned_id}%'))

    if project_name:
        query = query.filter(Project.project_name.ilike(f'%{project_name}%'))

    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(cast(Project.created_at, Date) >= start_date_obj)
        except ValueError:
            return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400

    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(cast(Project.created_at, Date) <= end_date_obj)
        except ValueError:
            return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400

    query = query.limit(10).offset(offset)

    projects = query.all()

    project_list = [{
        'id': p.id,
        'project_name': p.project_name,
        'project_subparts': p.project_subparts,
        'total_estimate_hrs': p.total_estimate_hrs,
        'total_elapsed_hrs': p.total_elapsed_hrs,
        'assigned_ids': p.assigned_ids,
        'is_completed': p.is_completed,
        'created_by': p.created_by,
        'client_id': p.client_id,
        'created_at': p.created_at,
        'updated_at': p.updated_at
    } for p in projects]

    return jsonify({'projects': project_list, 'total_projects': len(project_list)}), 200
