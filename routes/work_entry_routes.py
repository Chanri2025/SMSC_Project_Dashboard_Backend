from flask import Blueprint, request, jsonify
from models.work_day_entry import WorkDayEntry
from models.project import Project
from database import db
from datetime import datetime

work_day_entry_bp = Blueprint('work_day_entry_bp', __name__)


# ✅ Create a new work entry
@work_day_entry_bp.route('/create', methods=['POST'])
def create_work_entry():
    data = request.get_json()

    required_fields = ['user_id', 'hours_elapsed', 'project_name', 'project_subpart', 'assigned_by', 'assigned_to']

    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400

    if data['hours_elapsed'] > 8:
        return jsonify({'message': 'hours_elapsed cannot be more than 8'}), 400

    new_entry = WorkDayEntry(
        user_id=data['user_id'],
        work_date=datetime.strptime(data['work_date'], "%Y-%m-%d") if data.get('work_date') else datetime.utcnow(),
        hours_elapsed=data['hours_elapsed'],
        project_name=data['project_name'],
        project_subpart=data['project_subpart'],
        issues=data.get('issues', []),
        is_done=data.get('is_done', False),
        assigned_by=data['assigned_by'],
        assigned_to=data['assigned_to']
    )

    db.session.add(new_entry)

    # ✅ Update related project hours
    project = Project.query.filter_by(project_name=data['project_name']).first()
    if project:
        project.total_elapsed_hrs = (project.total_elapsed_hrs or 0) + data['hours_elapsed']

        updated_subparts = []
        for subpart in project.project_subparts:
            if subpart['project_subpart_name'] == data['project_subpart']:
                subpart['hours_elapsed'] = (subpart.get('hours_elapsed') or 0) + data['hours_elapsed']
            updated_subparts.append(subpart)

        project.project_subparts = updated_subparts
    print(project)

    db.session.commit()

    return jsonify({'message': 'Work Day Entry created successfully', 'id': new_entry.id}), 201


# ✅ Get all work entries
@work_day_entry_bp.route('/all', methods=['GET'])
def get_all_work_entries():
    entries = WorkDayEntry.query.order_by(WorkDayEntry.work_date.desc()).all()

    result = [{
        'id': e.id,
        'user_id': e.user_id,
        'work_date': e.work_date.strftime('%Y-%m-%d'),
        'hours_elapsed': e.hours_elapsed,
        'project_name': e.project_name,
        'project_subpart': e.project_subpart,
        'issues': e.issues,
        'is_done': e.is_done,
        'assigned_by': e.assigned_by,
        'assigned_to': e.assigned_to,
        'created_at': e.created_at,
        'updated_at': e.updated_at
    } for e in entries]

    return jsonify({'entries': result, 'total_entries': len(result)}), 200


# ✅ Update a work entry
@work_day_entry_bp.route('/update/<int:entry_id>', methods=['PUT'])
def update_work_entry(entry_id):
    entry = WorkDayEntry.query.get(entry_id)
    if not entry:
        return jsonify({'message': 'Work entry not found'}), 404

    data = request.get_json()
    old_hours = entry.hours_elapsed

    if 'hours_elapsed' in data:
        if data['hours_elapsed'] > 8:
            return jsonify({'message': 'hours_elapsed cannot be more than 8'}), 400
        entry.hours_elapsed = data['hours_elapsed']

    if 'project_name' in data:
        entry.project_name = data['project_name']

    if 'project_subpart' in data:
        entry.project_subpart = data['project_subpart']

    if 'issues' in data:
        entry.issues = data['issues']

    if 'is_done' in data:
        entry.is_done = data['is_done']

    db.session.commit()

    # ✅ After updating the work entry, update the related project
    project = Project.query.filter_by(project_name=entry.project_name).first()
    if project:
        diff = (entry.hours_elapsed or 0) - (old_hours or 0)
        project.total_elapsed_hrs = (project.total_elapsed_hrs or 0) + diff

        updated_subparts = []
        for subpart in project.project_subparts:
            if subpart['project_subpart_name'] == entry.project_subpart:
                subpart['hours_elapsed'] = (subpart.get('hours_elapsed') or 0) + diff
            updated_subparts.append(subpart)

        project.project_subparts = updated_subparts
        db.session.commit()

    return jsonify({'message': 'Work entry updated successfully'}), 200


# ✅ Filter work entries
@work_day_entry_bp.route('/filter', methods=['GET'])
def filter_work_entries():
    user_id = request.args.get('user_id', type=int)
    assigned_by = request.args.get('assigned_by', type=int)
    assigned_to = request.args.get('assigned_to', type=int)
    is_done = request.args.get('is_done', type=bool)
    project_name = request.args.get('project_name', type=str)

    query = WorkDayEntry.query

    if user_id:
        query = query.filter(WorkDayEntry.user_id == user_id)
    if assigned_by:
        query = query.filter(WorkDayEntry.assigned_by == assigned_by)
    if assigned_to:
        query = query.filter(WorkDayEntry.assigned_to == assigned_to)
    if is_done is not None:
        query = query.filter(WorkDayEntry.is_done == is_done)
    if project_name:
        query = query.filter(WorkDayEntry.project_name.ilike(f'%{project_name}%'))

    entries = query.order_by(WorkDayEntry.work_date.desc()).all()

    result = [{
        'id': e.id,
        'user_id': e.user_id,
        'work_date': e.work_date.strftime('%Y-%m-%d'),
        'hours_elapsed': e.hours_elapsed,
        'project_name': e.project_name,
        'project_subpart': e.project_subpart,
        'issues': e.issues,
        'is_done': e.is_done,
        'assigned_by': e.assigned_by,
        'assigned_to': e.assigned_to,
        'created_at': e.created_at,
        'updated_at': e.updated_at
    } for e in entries]

    return jsonify({'entries': result, 'total_entries': len(result)}), 200
