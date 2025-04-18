from flask import Blueprint, request, jsonify
from models.work_entry import WorkEntry
from models.employee import Employee
from database import db
from datetime import datetime

work_entry_bp = Blueprint('work_entry_bp', __name__)

@work_entry_bp.route('/submit', methods=['POST'])
def submit_entry():
    data = request.get_json()
    required_fields = ['employee_id', 'tasks', 'work_status']

    if any(field not in data or not data[field] for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400

    employee = Employee.query.filter_by(employee_id=data['employee_id']).first()
    if not employee:
        return jsonify({'message': 'Invalid employee ID'}), 404

    entry = WorkEntry(
        employee_id=employee.employee_id,
        full_name=employee.full_name,
        date=datetime.strptime(data.get('date'), '%Y-%m-%d') if data.get('date') else datetime.utcnow(),
        expected_date_of_delivery=datetime.strptime(data.get('expected_date_of_delivery'), '%Y-%m-%d') if data.get('expected_date_of_delivery') else None,
        work_status=data['work_status'],
        tasks=data['tasks'],
        issue=data.get('issue', '')
    )

    db.session.add(entry)
    db.session.commit()
    return jsonify(entry.id), 201

@work_entry_bp.route('/all', methods=['GET'])
def get_all_entries():
    entries = (
        db.session.query(WorkEntry, Employee)
        .join(Employee, Employee.employee_id == WorkEntry.employee_id)
        .order_by(WorkEntry.date.desc())
        .all()
    )
    result = [{
        'id': e.id,
        'employee_id': emp.employee_id,
        'full_name': emp.full_name,
        'date': e.date.strftime('%Y-%m-%d'),
        'expected_date_of_delivery': e.expected_date_of_delivery.strftime('%Y-%m-%d') if e.expected_date_of_delivery else None,
        'work_status': e.work_status,
        'tasks': e.tasks,
        'issue': e.issue
    } for e, emp in entries]

    return jsonify(result)
