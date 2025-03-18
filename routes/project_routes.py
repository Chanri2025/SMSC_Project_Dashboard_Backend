from flask import Blueprint, request, jsonify
from models.project import Project
from database import db

project_bp = Blueprint('project', __name__)


# ✅ Create a new project
@project_bp.route('/create', methods=['POST'])
def create_project():
    data = request.get_json()

    if not data or 'name' not in data or 'description' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    new_project = Project(
        name=data['name'],
        description=data['description']
    )
    db.session.add(new_project)
    db.session.commit()

    return jsonify({'message': 'Project created successfully', 'project_id': new_project.id}), 201


# ✅ Get all projects
@project_bp.route('/all', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    project_list = [{'id': p.id, 'name': p.name, 'description': p.description} for p in projects]

    return jsonify(project_list), 200


# ✅ Get a single project by ID
@project_bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = Project.query.get(project_id)

    if not project:
        return jsonify({'error': 'Project not found'}), 404

    return jsonify({'id': project.id, 'name': project.name, 'description': project.description}), 200


# ✅ Update project details
@project_bp.route('/update/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    project = Project.query.get(project_id)

    if not project:
        return jsonify({'error': 'Project not found'}), 404

    data = request.get_json()

    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']

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
