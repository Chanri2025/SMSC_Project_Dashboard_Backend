from flask import Blueprint, request, jsonify
from models.project import Project
from database import db
from datetime import datetime
from sqlalchemy import and_, cast, Date

project_bp = Blueprint('project', __name__)

# ✅ Create a new project (with employee_creator, update_logs, assigned employees)
@project_bp.route('/create', methods=['POST'])
def create_project():
    data = request.get_json()

    # Validate required fields
    required_fields = ['name', 'description', 'employee_creator']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields (name, description, employee_creator)'}), 400

    # Default assigned employees if not provided
    assigned_empids = data.get('assigned_empids', [])
    if not isinstance(assigned_empids, list):
        return jsonify({'error': 'assigned_empids must be an array'}), 400

    # Create new project with update logs
    new_project = Project(
        name=data['name'].strip(),
        description=data['description'].strip(),
        employee_creator=data['employee_creator'],
        assigned_empids=assigned_empids,
        update_logs=[{
            'updated_by': data['employee_creator'],
            'message': 'Project created',
            'timestamp': datetime.utcnow().isoformat()
        }]
    )

    db.session.add(new_project)
    db.session.commit()

    return jsonify({
        'message': 'Project created successfully',
        'project_id': new_project.id,
        'assigned_empids': new_project.assigned_empids,
        'update_logs': new_project.update_logs
    }), 201


# ✅ Get all projects (returns full details)
@project_bp.route('/all', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    project_list = [{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'employee_creator': p.employee_creator,
        'assigned_empids': p.assigned_empids,
        'update_logs': p.update_logs
    } for p in projects]

    return jsonify({'projects': project_list, 'total_projects': len(project_list)}), 200


# ✅ Get a single project by ID
@project_bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = Project.query.get(project_id)

    if not project:
        return jsonify({'error': 'Project not found'}), 404

    return jsonify({
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'employee_creator': project.employee_creator,
        'assigned_empids': project.assigned_empids,
        'update_logs': project.update_logs
    }), 200


# ✅ Update project details (updates update_logs automatically)
@project_bp.route('/update/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    project = Project.query.get(project_id)

    if not project:
        return jsonify({'error': 'Project not found'}), 404

    data = request.get_json()
    updated_by = data.get('updated_by')  # Required for logging updates

    if not updated_by:
        return jsonify({'error': 'updated_by field is required'}), 400

    changes = []

    if 'name' in data and data['name'] != project.name:
        project.name = data['name'].strip()
        changes.append('Updated name')

    if 'description' in data and data['description'] != project.description:
        project.description = data['description'].strip()
        changes.append('Updated description')

    if 'assigned_empids' in data and data['assigned_empids'] != project.assigned_empids:
        if not isinstance(data['assigned_empids'], list):
            return jsonify({'error': 'assigned_empids must be an array'}), 400
        project.assigned_empids = data['assigned_empids']
        changes.append('Updated assigned employees')

    # ✅ Append changes to update_logs
    if changes:
        project.add_update_log(updated_by, ', '.join(changes))

    db.session.commit()

    return jsonify({'message': 'Project updated successfully', 'update_logs': project.update_logs}), 200


# ✅ Delete a project
@project_bp.route('/delete/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    project = Project.query.get(project_id)

    if not project:
        return jsonify({'error': 'Project not found'}), 404

    db.session.delete(project)
    db.session.commit()

    return jsonify({'message': 'Project deleted successfully'}), 200


# ✅ Filter projects with different query parameters
@project_bp.route('/filter', methods=['GET'])
def filter_projects():
    # Get filter parameters from query string
    employee_creator = request.args.get('employee_creator', type=int)
    assigned_empid = request.args.get('assigned_empid', type=int)
    name = request.args.get('name', type=str)
    start_date = request.args.get('start_date', type=str)
    end_date = request.args.get('end_date', type=str)
    limit = request.args.get('limit', type=int, default=10)
    offset = request.args.get('offset', type=int, default=0)

    query = Project.query

    # Apply filters dynamically
    if employee_creator:
        query = query.filter(Project.employee_creator == employee_creator)

    if assigned_empid:
        query = query.filter(cast(Project.assigned_empids, str).like(f'%{assigned_empid}%'))

    if name:
        query = query.filter(Project.name.ilike(f'%{name}%'))  # Case-insensitive search

    # Handle Date Filters (if Project model has `created_at`)
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

    # Apply pagination
    query = query.limit(limit).offset(offset)

    projects = query.all()

    project_list = [{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'employee_creator': p.employee_creator,
        'assigned_empids': p.assigned_empids,
        'update_logs': p.update_logs
    } for p in projects]

    return jsonify({'projects': project_list, 'total_projects': len(project_list)}), 200
